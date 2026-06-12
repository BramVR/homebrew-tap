class Gohealthcli < Formula
  desc "Local-first, read-only Google Health archive CLI"
  homepage "https://github.com/BramVR/gohealthcli"
  version "0.1.0"
  license "MIT"

  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/BramVR/gohealthcli/releases/download/v0.1.0/gohealthcli_0.1.0_darwin_arm64.tar.gz"
      sha256 "7c326ff8629da80050e929952c3da6e380c79d60f9d9e72456eb9c433236208d"
    else
      url "https://github.com/BramVR/gohealthcli/releases/download/v0.1.0/gohealthcli_0.1.0_darwin_amd64.tar.gz"
      sha256 "b5a06f1a6b4361b24603112280522340895138af0dd921dadeb1dcffcbcccdc7"
    end
  end

  on_linux do
    if Hardware::CPU.arm? && Hardware::CPU.is_64_bit?
      url "https://github.com/BramVR/gohealthcli/releases/download/v0.1.0/gohealthcli_0.1.0_linux_arm64.tar.gz"
      sha256 "ec32605e6cbddc7fa15c378943d7980c7b5fe6ca63e199899a044ee280842987"
    end

    if Hardware::CPU.intel? && Hardware::CPU.is_64_bit?
      url "https://github.com/BramVR/gohealthcli/releases/download/v0.1.0/gohealthcli_0.1.0_linux_amd64.tar.gz"
      sha256 "8f9bcdb2a1bcc3fdc59c4d72020684f6105ee3aa173bfa3bc9a6e2c15eccf202"
    end
  end

  def install
    bin.install "gohealthcli"
  end

  def caveats
    <<~EOS
      Quick start:
        gohealthcli init
        gohealthcli doctor --plain

      Default local paths after init:
        ~/.config/gohealthcli/config.toml
        ~/.local/share/gohealthcli/gohealthcli.sqlite
    EOS
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/gohealthcli --version")
    assert_match "Initialise a fresh", shell_output("#{bin}/gohealthcli help init 2>&1")
  end
end
