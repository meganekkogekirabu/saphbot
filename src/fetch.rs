use crate::FetchArgs;
use bzip2::read::BzDecoder;
use futures_util::StreamExt;
use indicatif::{ProgressBar, ProgressStyle};
use reqwest::Client;
use std::{
    fs::{self, File},
    io::{Write, copy},
    os::unix::fs::symlink,
    path::Path,
};

pub async fn main(args: FetchArgs) -> anyhow::Result<()> {
    let filename = format!(
        "{}-latest-{}.xml.bz2",
        args.database.trim(),
        args.target.trim()
    );

    let base_url = format!(
        "https://{}/{}/latest/",
        args.root.trim(),
        args.database.trim()
    );
    let url = format!("{}{}", base_url, filename);

    fs::create_dir_all("../dumps")?;
    let output_path = format!("../dumps/{}", filename);
    let decompressed_path = output_path.strip_suffix(".bz2").unwrap_or(&output_path);

    println!("Downloading: {}", url);

    let client = Client::new();
    let response = client.get(&url).send().await?.error_for_status()?;

    let total_size = response.content_length();
    let mut dest = File::create(&output_path)?;

    let pb = if !args.disable_progress {
        if let Some(size) = total_size {
            let pb = ProgressBar::new(size);
            pb.set_style(
                ProgressStyle::with_template(
                    "{msg:20} [{bar:40.cyan/blue}] {bytes}/{total_bytes} ({eta})",
                )?
                .progress_chars("=> "),
            );
            pb.set_message(filename.chars().take(20).collect::<String>());
            Some(pb)
        } else {
            let pb = ProgressBar::new_spinner();
            pb.enable_steady_tick(std::time::Duration::from_millis(100));
            pb.set_message("Downloading...");
            Some(pb)
        }
    } else {
        None
    };

    let mut downloaded = 0u64;
    let mut stream = response.bytes_stream();

    while let Some(Ok(chunk)) = stream.next().await {
        dest.write_all(&chunk)?;
        downloaded += chunk.len() as u64;
        if let Some(ref pb) = pb {
            pb.set_position(downloaded);
        }
    }

    if let Some(pb) = pb {
        pb.finish_with_message("Download complete");
    }

    println!("Decompressing...");

    let compressed_file = File::open(&output_path)?;
    let mut decompressor = BzDecoder::new(compressed_file);
    let mut decompressed_file = File::create(decompressed_path)?;
    copy(&mut decompressor, &mut decompressed_file)?;

    fs::remove_file(&output_path)?;

    let latest_link = Path::new("latest.xml");
    if latest_link.exists() {
        fs::remove_file(latest_link)?;
    }

    symlink(decompressed_path, latest_link)?;

    Ok(())
}
