/*
* Tool for grepping MediaWiki pages-meta-current dumps.
*
* Copyright (c) 2025 Choi Madeleine
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

use anyhow::Context;
use clap::Parser;
use indicatif::{ProgressBar, ProgressStyle};
use quick_xml::{Reader, events::Event};
use regex::{Match, Regex, RegexBuilder};
use std::{
    fs::File,
    io::{BufRead, BufWriter, Write},
    time::Duration,
};

pub struct GrepConfig<'a> {
    pub query: &'a str,
    pub case_insensitive: bool,
    pub pagename: bool,
    pub namespaces: Option<Vec<u32>>,
    pub invert_namespaces: Option<bool>,
}

fn _grep<R, F>(
    config: GrepConfig,
    progress: &mut Option<ProgressBar>,
    mut callback: F,
    reader: &mut Reader<R>,
) -> anyhow::Result<u32>
where
    F: FnMut(&str, &Match<'_>, &u32),
    R: BufRead,
{
    let mut buf = Vec::new();

    let mut tag = "";
    let mut title = String::new();
    let mut text = String::new();
    let mut ns: u32 = 0;

    let mut re: Option<Regex> = None;

    if !config.pagename {
        re = Some(
            RegexBuilder::new(config.query)
                .case_insensitive(config.case_insensitive)
                .build()?,
        );
    }

    let check_ns = config.invert_namespaces.is_some() && config.namespaces.is_some();
    let mut n = 0u32;

    loop {
        match reader.read_event_into(&mut buf) {
            Ok(Event::Start(ref e)) => match e.name().as_ref() {
                b"text" => tag = "text",
                b"ns" => tag = "ns",
                b"title" => tag = "title",
                _ => {}
            },
            Ok(Event::End(ref e)) => match e.name().as_ref() {
                b"page" => {
                    if let Some(p) = progress.as_mut() {
                        p.inc(1);
                    }

                    if config.pagename {
                        re = Some(
                            RegexBuilder::new(&config.query.replace("<<PAGENAME>>", &title))
                                .case_insensitive(config.case_insensitive)
                                .build()?,
                        );
                    }

                    if check_ns {
                        let invert = config.invert_namespaces.unwrap_or(false);
                        let matches = config.namespaces.as_ref().is_some_and(|n| n.contains(&ns));

                        if invert == matches {
                            title.clear();
                            text.clear();
                            continue;
                        }
                    }

                    if let Some(mat) = re.as_ref().unwrap().find(&text) {
                        n += 1;
                        callback(&title, &mat, &n);
                        if let Some(p) = progress.as_mut() {
                            p.set_message(format!("{n}"));
                        }
                    }

                    title.clear();
                    text.clear();
                }
                _ => tag = "",
            },
            Ok(Event::Text(ref e)) => {
                let content = e.xml_content().unwrap().into_owned();

                match tag {
                    "title" => title.push_str(&content),
                    "text" => text.push_str(&content),
                    "ns" => {
                        ns = content
                            .parse()
                            .with_context(|| "could not parse namespace into u32")
                            .unwrap();
                    }
                    _ => {}
                }
            }
            Ok(Event::Eof) => break,
            Err(e) => panic!("error: {e:#?}"),
            _ => {}
        }
        buf.clear();
    }

    Ok(n)
}

#[derive(Parser, Debug)]
#[command(
    version,
    about,
    long_about = "0.1.0
Copyright (c) 2025 Choi Madeleine <gankiann.niu@gmail.com>
License GPLv3+: GNU GPL version 3 or later <https://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law."
)]
struct Args {
    query: String,

    #[arg(
        short,
        long,
        help = "if enabled, prints out a count of matching pages rather than a list of titles"
    )]
    count: bool,

    #[arg(
        short = 'i',
        long,
        help = "if enabled, page text must match case of query"
    )]
    case_insensitive: bool,

    #[arg(long, help = "disables progress display")]
    disable_progress: bool,

    #[arg(
        short,
        long,
        default_value = "../dumps/latest.xml",
        help = "file to read from"
    )]
    file: String,

    #[arg(
        long,
        default_value = "500",
        help = "how often to flush output; set this to 1 to fix choppiness with printing the results, but will be slower"
    )]
    flush_rate: u32,

    #[arg(
        long,
        default_value = "\x1b[34m\x1b[4;34m$1\x1b[0m matches at position \x1b[31m$2\x1b[0m",
        hide_default_value = true,
        help = "formatting string to output titles in, accepting `$1' for the title, `$2' for the match range, and `$3' for the count"
    )]
    format: String,

    #[arg(
        long,
        help = "if enabled, excludes namespaces in `--namespaces' rather than including them"
    )]
    invert_namespaces: bool,

    #[arg(
        short,
        long,
        value_delimiter = ',',
        help = "a comma-separated list of namespaces"
    )]
    namespaces: Option<Vec<u32>>,

    #[arg(short, long, help = "output file (defaults to stdout)")]
    output: Option<String>,

    #[arg(
        long,
        help = "if enabled, `<<PAGENAME>>' in the query is dynamically substituted for the pagename for each page"
    )]
    pagename: bool,
}

fn main() -> anyhow::Result<()> {
    let args = Args::parse();

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

    let n = _grep(
        GrepConfig {
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
