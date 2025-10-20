use anyhow::Context;
use indicatif::ProgressBar;
use quick_xml::{Reader, events::Event};
use regex::{Match, Regex, RegexBuilder};
use std::io::BufRead;

pub struct GrepConfig<'a> {
    pub query: &'a str,
    pub case_insensitive: bool,
    pub pagename: bool,
    pub namespaces: Option<Vec<u32>>,
    pub invert_namespaces: Option<bool>,
}

pub fn grep<R, F>(
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
