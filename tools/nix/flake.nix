{
  description = "repository-template";

  nixConfig = {
    extra-trusted-substituters = [
      # Nix community's cache server
      "https://nix-community.cachix.org"
      "https://devenv.cachix.org"
    ];
    extra-trusted-public-keys = [
      "nix-community.cachix.org-1:mB9FSh9qf2dCimDSUo8Zy7bkq5CX+/rkCWyvRCYg3Fs="
      "devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw="
    ];
  };

  inputs = {
    # Nixpkgs repository.
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

    # Format the repo with nix-treefmt.
    treefmt-nix = {
      url = "github:numtide/treefmt-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    # The devenv module to create good development shells.
    devenv = {
      url = "github:cachix/devenv/latest";
      inputs.nixpkgs.follows = "nixpkgsDevenv";
    };
    # We should lock the pkgs in `mkShell` here:
    # https://github.com/cachix/devenv/issues/1797
    # to devenvs rolling nixpkgs. Note: that does not restrict the use of
    # 'nixpkgs' input in devenv modules.
    nixpkgsDevenv.url = "github:cachix/devenv-nixpkgs/rolling";

    # Snowfall provides a structured way of creating a flake output.
    # Documentation: https://snowfall.org/guides/lib/quickstart/
    snowfall-lib = {
      url = "github:snowfallorg/lib?ref=v3.0.3";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    # The Python packages for all versions.
    nixpkgs-python = {
      url = "github:cachix/nixpkgs-python";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    inputs:
    let
      root-dir = ../..;
    in
    inputs.snowfall-lib.mkFlake {
      inherit inputs;
      # The `src` must be the root of the flake.
      src = "${root-dir}";

      snowfall = {
        root = "${root-dir}" + "/tools/nix";
        namespace = "repository";
        meta = {
          name = "strings-to-things";
          title = "This a repository turns strings into things";
        };
      };
    };
}
