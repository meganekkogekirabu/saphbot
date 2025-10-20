use crate::SearchArgs;
use indicatif::{ProgressBar, ProgressStyle};
use quick_xml::Reader;
use regex::Match;
use std::{
    fs::File,
    io::{BufWriter, Write},
    time::Duration,
};

mod pages_meta_current;

pub fn main(args: SearchArgs) -> anyhow::Result<()> {
    let mut output: BufWriter<Box<dyn Write>>;

    let mut progress: Option<ProgressBar> = None;

    if args.flush_rate > 10 && !args.disable_progress {
        progress = Some(ProgressBar::new_spinner());
        progress
            .as_mut()
            .unwrap()
            .enable_steady_tick(Duration::from_millis(200));
        progress.as_mut().unwrap().set_style(
            ProgressStyle::with_template(
                "{spinner} {msg}/{pos} pages [{elapsed_precise} elapsed; {per_sec:!}]",
            )
            .unwrap()
            .progress_chars("##-"),
        );
    }

    if let Some(filename) = args.output {
        let file = File::create(filename)?;
        output = BufWriter::new(Box::new(file));
    } else {
        let stdout = std::io::stdout();
        output = BufWriter::new(Box::new(stdout.lock()));
    }

    let callback = |title: &str, mat: &Match<'_>, n: &u32| {
        let out = args
            .format
            .replace("$1", title)
            .replace("$2", &format!("{:?}", mat.range()));

        writeln!(output, "{out}").unwrap();

        if n % args.flush_rate == 0 {
            output.flush().unwrap();
        }
    };

    let mut reader = Reader::from_file(args.file)?;

    let n = pages_meta_current::grep(
        pages_meta_current::GrepConfig {
            query: &args.query,
            case_insensitive: args.case_insensitive,
            pagename: args.pagename,
            namespaces: args.namespaces,
            invert_namespaces: args.invert_namespaces.then_some(true),
        },
        &mut progress,
        callback,
        &mut reader,
    )?;

    output.flush()?;
    drop(reader);
    drop(output);

    if args.count {
        println!("Counted {n} pages which matched the query");
    }

    progress.unwrap().finish();

    Ok(())
}
