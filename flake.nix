{
  description = "manim";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config = {
            allowUnfree = true;
          };
        };
        python = pkgs.python312Packages.python;
        pythonEnv = python.withPackages (ps: with ps; [
          pandas
          matplotlib
          numpy
          scipy
		  manim
		  manim-slides
		  #pyqt5
		  pyqt5-multimedia
          #jupyterlab  # Include JupyterLab in pythonEnv
          ipykernel   # Include ipykernel to register kernels
        ]);
      in
      {
        devShell = pkgs.mkShell {
          buildInputs = with pkgs; [
            pythonEnv
			watchexec
			mpv
            qt5.qtbase  # Add Qt libraries - for manim-slides
            qt5.qtwayland # Needed to make python display plots on wayland
            libsForQt5.qt5.qtmultimedia
			manim-slides
			#manim
          ];
        };
		
        shellHook = ''
          python -m ipykernel install --user --name=python-env --display-name="Python (Env)"
		  echo "Welcome to nix shell"
        '';
      }
    );
}
