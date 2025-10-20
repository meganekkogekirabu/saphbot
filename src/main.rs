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

use clap::{Parser, Subcommand};

mod fetch;
mod search;

#[derive(Parser, Debug)]
pub struct SearchArgs {
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

#[derive(Parser, Debug)]
pub struct FetchArgs {
    #[arg(short, long, default_value = "enwiki", help = "database name")]
    database: String,

    #[arg(long, help = "disables progress display")]
    disable_progress: bool,

    #[arg(
        long,
        default_value = "dumps.wikimedia.org",
        help = "root URL for downloading dumps from (without http(s)://)"
    )]
    root: String,

    #[arg(
        short,
        long,
        default_value = "pages-meta-current",
        help = "target dump"
    )]
    target: String,
}

#[derive(Subcommand, Debug)]
pub enum Commands {
    Search(SearchArgs),
    Fetch(FetchArgs),
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
    #[command(subcommand)]
    cmd: Commands,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let cli = Args::parse();

    match cli.cmd {
        Commands::Search(args) => {
            search::main(args)?;
        }
        Commands::Fetch(args) => {
            fetch::main(args).await?;
        }
    }

    Ok(())
}
