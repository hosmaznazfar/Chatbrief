use clap::{Parser, Subcommand};
use serde::{Deserialize, Serialize};
use std::{env, fs, io::{self, IsTerminal, Write}, path::{Component, Path, PathBuf}, process::{Command, Stdio}, thread, time::{Duration, Instant}};

const CONFIG: &str = ".pj/workflow.toml";
const START: &str = "<!-- pj:dependencies:start -->";
const END: &str = "<!-- pj:dependencies:end -->";

#[derive(Parser)]
#[command(name="pj", version, about="Project setup and ordered multi-language checks")]
struct Cli { #[command(subcommand)] command: Commands }
#[derive(Subcommand)]
enum Commands {
    Init,
    Doctor,
    Check {
        #[arg(long, value_name="COMMAND", conflicts_with_all=["dry_run","list","remove"])] add_command: Option<String>,
        #[arg(long, conflicts_with_all=["add_command","list","remove"])] dry_run: bool,
        #[arg(long, conflicts_with_all=["add_command","dry_run","remove"])] list: bool,
        #[arg(long, value_name="NAME", conflicts_with_all=["add_command","dry_run","list"])] remove: Option<String>,
    },
    Workflow { #[command(subcommand)] action: WorkflowAction },
}
#[derive(Subcommand)]
enum WorkflowAction { Validate }
#[derive(Debug, Clone, Serialize, Deserialize)]
struct Config {
    #[serde(default="schema_version")] schema_version: u32,
    #[serde(default)] project: Project,
    #[serde(default)] checks: Checks,
}
fn schema_version()->u32{1}
impl Default for Config { fn default()->Self { Self { schema_version: 1, project: Project::default(), checks: Checks::default() } } }
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
struct Project { #[serde(default)] name:String }
#[derive(Debug, Clone, Serialize, Deserialize)]
struct Checks { #[serde(default="yes")] fail_fast:bool, #[serde(default)] steps:Vec<Step> }
impl Default for Checks { fn default()->Self{Self{fail_fast:true,steps:vec![]}} }
fn yes()->bool{true}
#[derive(Debug, Clone, Serialize, Deserialize)]
struct Step {
    name:String, command:String, #[serde(default)] args:Vec<String>,
    #[serde(default)] cwd:Option<String>, #[serde(default="yes")] required:bool,
    #[serde(default)] timeout_seconds:Option<u64>, #[serde(default)] requires:Vec<String>,
    #[serde(default)] description:Option<String>,
}
fn main(){if let Err(e)=dispatch(){eprintln!("[pj] error: {e}");std::process::exit(1)}}
fn dispatch()->Result<(),String>{
    let cli=Cli::parse();let root=env::current_dir().map_err(|e|e.to_string())?;
    match cli.command{
        Commands::Init=>init(&root),Commands::Doctor=>doctor(&root),
        Commands::Check{add_command,dry_run,list,remove}=>{
            if let Some(s)=add_command{add_check(&root,&s)}
            else if let Some(s)=remove{remove_check(&root,&s)}
            else if list{list_checks(&root)}else{run_checks(&root,dry_run)}
        },
        Commands::Workflow{action:WorkflowAction::Validate}=>{
            let(_,c)=load(&root)?;validate(&c,&root)?;
            println!("Workflow configuration valid ({} checks).",c.checks.steps.len());Ok(())
        }
    }
}
fn config_path(r:&Path)->PathBuf{r.join(CONFIG)}
fn load(r:&Path)->Result<(PathBuf,Config),String>{
    let p=config_path(r);let raw=fs::read_to_string(&p).map_err(|e|format!("cannot read {}: {e}; run pj init first",p.display()))?;
    let c=toml::from_str(&raw).map_err(|e|format!("invalid TOML in {}: {e}",p.display()))?;Ok((p,c))
}
fn save(p:&Path,c:&Config)->Result<(),String>{
    let s=toml::to_string_pretty(c).map_err(|e|e.to_string())?;
    fs::write(p,format!("# Project-local AIWorkFlow configuration. Review commands before running.\n{s}")).map_err(|e|e.to_string())
}
fn validate(c:&Config,r:&Path)->Result<(),String>{
    if c.schema_version!=1{return Err(format!("unsupported schema_version {}; expected 1",c.schema_version))}
    for (i,s) in c.checks.steps.iter().enumerate(){
        if s.name.trim().is_empty()||s.command.trim().is_empty(){return Err(format!("check {} needs name and command",i+1))}
        if let Some(cwd)=&s.cwd{
            let p=Path::new(cwd);
            if p.is_absolute()||p.components().any(|x|matches!(x,Component::ParentDir|Component::RootDir|Component::Prefix(_))){return Err(format!("check '{}' cwd must stay inside project",s.name))}
            if !r.join(p).is_dir(){return Err(format!("check '{}' cwd does not exist: {cwd}",s.name))}
        }
        if s.timeout_seconds==Some(0){return Err(format!("check '{}' timeout must be positive",s.name))}
    }Ok(())
}
fn mkstep(n:&str,c:&str,a:Vec<String>)->Step{Step{name:n.into(),command:c.into(),args:a,cwd:None,required:true,timeout_seconds:Some(900),requires:vec![],description:Some("Detected from project metadata; review before execution.".into())}}
fn detect_checks(r:&Path)->Vec<Step>{
    let mut v=vec![];
    if let Ok(raw)=fs::read_to_string(r.join("package.json")){
        if let Ok(j)=serde_json::from_str::<serde_json::Value>(&raw){
            if j.get("scripts").and_then(|s|s.get("test")).and_then(|x|x.as_str()).is_some(){
                let(c,a)=if r.join("pnpm-lock.yaml").exists(){("pnpm",vec!["run","test"])}else if r.join("yarn.lock").exists(){("yarn",vec!["test"])}else if r.join("bun.lock").exists()||r.join("bun.lockb").exists(){("bun",vec!["run","test"])}else{("npm",vec!["run","test"])};
                v.push(mkstep("node-tests",c,a.into_iter().map(str::to_owned).collect()));
            }
        }
    }
    if r.join("Cargo.toml").is_file(){v.push(mkstep("rust-tests","cargo",vec!["test".into()]))}
    if r.join("go.mod").is_file(){v.push(mkstep("go-tests","go",vec!["test".into(),"./...".into()]))}
    if let Ok(py)=fs::read_to_string(r.join("pyproject.toml")){if py.contains("pytest"){
        let(c,a)=if has_exe("uv"){("uv",vec!["run".into(),"pytest".into()])}else{(if has_exe("python3"){"python3"}else{"python"},vec!["-m".into(),"pytest".into()])};v.push(mkstep("python-tests",c,a));
    }}
    if let Ok(es)=fs::read_dir(r){for e in es.flatten(){let p=e.path();if p.extension().is_some_and(|x|x=="sln"||x=="slnx"){
        if let Some(n)=p.file_name().and_then(|x|x.to_str()){v.push(mkstep("dotnet-tests","dotnet",vec!["test".into(),n.into()]));break}
    }}}
    v
}
fn init(r:&Path)->Result<(),String>{
    let p=config_path(r);
    if p.exists(){let(_,c)=load(r)?;validate(&c,r)?;println!("[pj init] Existing config valid; preserving it.");}
    else{fs::create_dir_all(p.parent().unwrap()).map_err(|e|e.to_string())?;let mut c=Config::default();c.project.name=r.file_name().and_then(|x|x.to_str()).unwrap_or("project").into();c.checks.steps=detect_checks(r);save(&p,&c)?;println!("[pj init] Created {} with {} detected check(s).",p.display(),c.checks.steps.len());}
    update_readme(r)?;doctor(r)?;offer_integrations()?;println!("[pj init] Review .pj/workflow.toml and README.md before running checks.");Ok(())
}
fn has_exe(n:&str)->bool{
    if Path::new(n).components().count()>1{return Path::new(n).is_file()}
    env::var_os("PATH").map(|ps|env::split_paths(&ps).any(|p|{
        if p.join(n).is_file(){return true}
        #[cfg(windows)] for ext in ["exe","cmd","bat"]{if p.join(format!("{n}.{ext}")).is_file(){return true}}
        false
    })).unwrap_or(false)
}
fn doctor(r:&Path)->Result<(),String>{
    println!("[pj doctor] {}",r.display());
    for(f,l)in[("package.json","Node.js"),("Cargo.toml","Rust"),("pyproject.toml","Python"),("go.mod","Go")]{if r.join(f).is_file(){println!(" detected: {l} ({f})")}}
    if fs::read_dir(r).map(|es|es.flatten().any(|e|e.path().extension().is_some_and(|x|x=="sln"||x=="slnx"||x=="csproj"))).unwrap_or(false){println!(" detected: .NET")}
    for t in ["git","uv","graphify","node","npm","pnpm","yarn","bun","python","python3","cargo","rustc","dotnet","go"]{println!(" {:<9} {}",t,if has_exe(t){"available"}else{"not found"})}
    if r.join("package.json").is_file() && !has_exe("node") { println!(" guidance: install Node.js from https://nodejs.org/en/download/"); }
    if r.join("Cargo.toml").is_file() && !has_exe("cargo") { println!(" guidance: install Rust/Cargo from https://www.rust-lang.org/tools/install"); }
    if r.join("pyproject.toml").is_file() && !has_exe("python") && !has_exe("python3") { println!(" guidance: install Python from https://www.python.org/downloads/"); }
    if r.join("go.mod").is_file() && !has_exe("go") { println!(" guidance: install Go from https://go.dev/doc/install"); }
    if fs::read_dir(r).map(|es|es.flatten().any(|e|e.path().extension().is_some_and(|x|x=="sln"||x=="slnx"||x=="csproj"))).unwrap_or(false) && !has_exe("dotnet") { println!(" guidance: install the .NET SDK from https://dotnet.microsoft.com/en-us/download"); }
    println!(" config    {}",if config_path(r).exists(){CONFIG}else{"not initialized"});Ok(())
}
fn confirm(q:&str)->Result<bool,String>{print!("{q} [y/N] ");io::stdout().flush().map_err(|e|e.to_string())?;let mut s=String::new();io::stdin().read_line(&mut s).map_err(|e|e.to_string())?;Ok(matches!(s.trim().to_ascii_lowercase().as_str(),"y"|"yes"))}
fn offer_integrations()->Result<(),String>{
    if !io::stdin().is_terminal(){println!("[pj init] Non-interactive: skipped optional install prompts.");return Ok(())}
    if !has_exe("uv"){
        println!("[pj init] uv missing. Official instructions: https://docs.astral.sh/uv/getting-started/installation/");
        if confirm("Try installing uv using Python pip (python -m pip install --user uv) if available?")?{
            let py=if has_exe("python3"){"python3"}else{"python"};
            if has_exe(py){let s=Command::new(py).args(["-m","pip","install","--user","uv"]).status().map_err(|e|e.to_string())?;if !s.success(){println!("uv install failed; follow official instructions.")}}
            else{println!("Python unavailable; install uv using official instructions.")}
        }
    }
    if !has_exe("graphify"){
        println!("[pj init] Graphify is optional; package name is graphifyy.");
        if has_exe("uv")&&confirm("Install Graphify with uv tool install graphifyy?")?{
            let s=Command::new("uv").args(["tool","install","graphifyy"]).status().map_err(|e|e.to_string())?;if !s.success(){println!("Graphify install failed; see https://graphiffy.com/docs/install")}
        }else if !has_exe("uv"){println!("Install uv first, then run: uv tool install graphifyy")}
    }else{println!("[pj init] Graphify installed; graphify install and graph generation are separate steps.")}
    Ok(())
}
fn manifests(r:&Path)->Vec<String>{
    let mut v=vec![];for(f,l)in[("package.json","Node.js"),("Cargo.toml","Rust"),("pyproject.toml","Python"),("go.mod","Go")]{if r.join(f).is_file(){v.push(l.to_string())}}
    if fs::read_dir(r).map(|es|es.flatten().any(|e|e.path().extension().is_some_and(|x|x=="sln"||x=="slnx"))).unwrap_or(false){v.push(".NET".into())}
    if v.is_empty(){v.push("no supported project manifest detected".into())}v
}
fn update_readme(r:&Path)->Result<(),String>{
    let p=r.join("README.md");let mut s=if p.exists(){fs::read_to_string(&p).map_err(|e|e.to_string())?}else{"# Project\n\n".into()};
    let check_summary=match load(r){Ok((_,c)) if !c.checks.steps.is_empty()=>c.checks.steps.iter().map(|x|format!("- {}: {} {}",x.name,x.command,x.args.join(" "))).collect::<Vec<_>>().join("\n"),_=>"- No conventional test command detected. Add one with pj check --add-command \"npm run test\" or edit .pj/workflow.toml.".into()};
    let tools=["node","npm","python","python3","uv","cargo","dotnet","go","graphify"].iter().map(|x|format!("- {}: {}",x,if has_exe(x){"available"}else{"not found"})).collect::<Vec<_>>().join("\n");
    let block=format!("{START}\n## Detected development tools and checks\n\nGenerated by pj init. Review this section as the project changes.\n\n- Workflow config: .pj/workflow.toml\n- Run checks in order: pj check\n- Add a check without running it: pj check --add-command \"npm run test\"\n- Validate config: pj workflow validate\n\nDetected project manifests: {}\n\nDetected checks (review before running):\n{}\n\nTool availability:\n{}\n\nOptional integrations:\n- uv: see https://docs.astral.sh/uv/getting-started/installation/.\n- Graphify: optional tooling; install with uv tool install graphifyy. Configure assistant integration separately.\n{END}",manifests(r).join(", "),check_summary,tools);
    if let Some(i)=s.find(START){let tail=&s[i+START.len()..];let off=tail.find(END).ok_or("README has pj start marker but no end marker; refusing to overwrite")?;s.replace_range(i..i+START.len()+off+END.len(),&block);}
    else{if !s.ends_with('\n'){s.push('\n')}s.push('\n');s.push_str(&block);s.push('\n')}
    fs::write(p,s).map_err(|e|format!("cannot update README.md: {e}"))
}
fn tokenize(raw:&str)->Result<Vec<String>,String>{
    let mut out=vec![];let mut cur=String::new();let mut quote=None;let mut escaped=false;
    for c in raw.chars(){
        if escaped{cur.push(c);escaped=false;continue}
        if c=='\\'&&quote!=Some('\''){escaped=true;continue}
        if let Some(q)=quote{if c==q{quote=None}else{cur.push(c)};continue}
        if c=='\''||c=='"'{quote=Some(c);continue}
        if c.is_whitespace(){if !cur.is_empty(){out.push(std::mem::take(&mut cur))}continue}
        if ";&|<>$".contains(c)||c=='\u{60}'{return Err("shell operators are not allowed in --add-command; configure a reviewed explicit shell invocation in TOML".into())}
        cur.push(c);
    }
    if escaped{cur.push('\\')}if quote.is_some(){return Err("unclosed quote in command".into())}if !cur.is_empty(){out.push(cur)}Ok(out)
}
fn add_check(r:&Path,raw:&str)->Result<(),String>{
    let t=tokenize(raw)?;if t.is_empty(){return Err("provide a command such as npm run test".into())}
    let(_,mut c)=load(r)?;let command=t[0].clone();let args=t[1..].to_vec();
    let name=std::iter::once(command.as_str()).chain(args.iter().map(String::as_str)).collect::<Vec<_>>().join("-").chars().map(|x|if x.is_ascii_alphanumeric(){x.to_ascii_lowercase()}else{'-'}).collect::<String>().trim_matches('-').to_string();
    let name=if name.is_empty(){format!("check-{}",c.checks.steps.len()+1)}else{name};
    if c.checks.steps.iter().any(|x|x.name==name){return Err(format!("check '{name}' already exists"))}
    c.checks.steps.push(Step{name:name.clone(),command,args,cwd:None,required:true,timeout_seconds:Some(900),requires:vec![],description:Some("Added by pj; review before running.".into())});
    validate(&c,r)?;save(&config_path(r),&c)?;println!("Added '{name}' to ordered checks; not executed.");Ok(())
}
fn list_checks(r:&Path)->Result<(),String>{let(_,c)=load(r)?;validate(&c,r)?;if c.checks.steps.is_empty(){println!("No checks configured.")}for(i,s)in c.checks.steps.iter().enumerate(){println!("{}. {}: {} {}{}",i+1,s.name,s.command,s.args.join(" "),s.cwd.as_ref().map(|x|format!(" (cwd: {x})")).unwrap_or_default())}Ok(())}
fn remove_check(r:&Path,n:&str)->Result<(),String>{let(p,mut c)=load(r)?;let len=c.checks.steps.len();c.checks.steps.retain(|s|s.name!=n);if len==c.checks.steps.len(){return Err(format!("no check named '{n}'"))}save(&p,&c)?;println!("Removed check '{n}'.");Ok(())}
fn run_checks(r:&Path,dry:bool)->Result<(),String>{
    let(_,c)=load(r)?;validate(&c,r)?;if c.checks.steps.is_empty(){println!("No checks configured. Add one with pj check --add-command \"npm run test\".");return Ok(())}
    let mut failed=false;
    for s in &c.checks.steps{
        let cwd=s.cwd.as_ref().map(|x|r.join(x)).unwrap_or_else(||r.to_path_buf());let line=std::iter::once(s.command.as_str()).chain(s.args.iter().map(String::as_str)).collect::<Vec<_>>().join(" ");
        if dry{println!("[dry-run] ({}) {line}",cwd.display());continue}
        let missing=s.requires.iter().filter(|x|!has_exe(x)).cloned().collect::<Vec<_>>();
        if !missing.is_empty(){println!("SKIP {}: missing {}",s.name,missing.join(", "));if s.required{failed=true;if c.checks.fail_fast{break}}continue}
        if !has_exe(&s.command){println!("{}: executable '{}' not found",if s.required{"FAIL"}else{"SKIP"},s.command);if s.required{failed=true;if c.checks.fail_fast{break}}continue}
        println!("\n[pj check] {}: {line}",s.name);
        let result=match Command::new(&s.command).args(&s.args).current_dir(&cwd).stdin(Stdio::inherit()).stdout(Stdio::inherit()).stderr(Stdio::inherit()).spawn(){
            Err(e)=>{eprintln!("could not start {}: {e}",s.command);false}
            Ok(mut child)=>if let Some(secs)=s.timeout_seconds{let start=Instant::now();loop{match child.try_wait(){
                Ok(Some(st))=>break st.success(),
                Ok(None)if start.elapsed()<Duration::from_secs(secs)=>thread::sleep(Duration::from_millis(100)),
                Ok(None)=>{let _=child.kill();let _=child.wait();eprintln!("{} timed out after {secs}s",s.name);break false}
                Err(e)=>{eprintln!("wait failed: {e}");break false}
            }}}else{child.wait().map(|x|x.success()).unwrap_or(false)}
        };
        if result{println!("PASS {}",s.name)}else{println!("FAIL {}",s.name);if s.required{failed=true;if c.checks.fail_fast{break}}}
    }
    if failed{Err("one or more required checks failed".into())}else{Ok(())}
}
#[cfg(test)]mod tests{
    use super::*;use tempfile::tempdir;
    #[test]fn quoted_args(){assert_eq!(tokenize(r#"npm run "test:unit""#).unwrap(),vec!["npm","run","test:unit"])}
    #[test]fn shell_operators_rejected(){assert!(tokenize("cargo test && echo unsafe").is_err());assert!(tokenize("npm test | tee log").is_err())}
    #[test]fn unclosed_quote_rejected(){assert!(tokenize(r#"npm run "test"#).is_err())}
    #[test]fn config_round_trip(){let d=tempdir().unwrap();fs::create_dir(d.path().join(".pj")).unwrap();let mut c=Config::default();c.checks.steps.push(mkstep("tests","cargo",vec!["test".into()]));save(&d.path().join(CONFIG),&c).unwrap();let(_,x)=load(d.path()).unwrap();validate(&x,d.path()).unwrap();assert_eq!(x.checks.steps.len(),1)}
    #[test]fn cwd_cannot_escape(){let d=tempdir().unwrap();let mut c=Config::default();let mut s=mkstep("bad","echo",vec![]);s.cwd=Some("../outside".into());c.checks.steps.push(s);assert!(validate(&c,d.path()).is_err())}
    #[test]fn detects_multiple_languages_in_stable_order(){let d=tempdir().unwrap();fs::write(d.path().join("package.json"),r#"{"scripts":{"test":"jest"}}"#).unwrap();fs::write(d.path().join("Cargo.toml"),"[package]").unwrap();fs::write(d.path().join("go.mod"),"module example").unwrap();fs::write(d.path().join("pyproject.toml"),"[project]\ndependencies = [\"pytest\"]").unwrap();fs::write(d.path().join("Example.sln"),"").unwrap();let steps=detect_checks(d.path());assert_eq!(steps.iter().map(|x|x.name.as_str()).collect::<Vec<_>>(),vec!["node-tests","rust-tests","go-tests","python-tests","dotnet-tests"])}
    #[test]fn readme_idempotent_and_preserves_text(){let d=tempdir().unwrap();fs::write(d.path().join("README.md"),"# Keep me\n\nExisting content.\n").unwrap();update_readme(d.path()).unwrap();let a=fs::read_to_string(d.path().join("README.md")).unwrap();update_readme(d.path()).unwrap();let b=fs::read_to_string(d.path().join("README.md")).unwrap();assert!(a.starts_with("# Keep me\n\nExisting content."));assert_eq!(a,b)}
}
