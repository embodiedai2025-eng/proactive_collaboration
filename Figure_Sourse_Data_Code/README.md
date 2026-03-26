# Figure Source Data Code

This repository contains standalone scripts to reproduce figures from embedded data.

## Environment Setup

Use Python 3.10+ (3.11 recommended).

```bash
python -m venv .venv
```

Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install matplotlib numpy pandas plotly kaleido cycler
```

## Reproduce Figures

Run each script from the repository root:

```bash
python Main_Figure_4_lower/generate_main_figure_4_lower.py
python Main_Figure_6_upper/generate_main_figure_6_upper.py
python Main_Figure_7_lower/generate_main_figure_7_lower.py
python Main_Figure_8/generate_main_figure_8.py
python Supp_Figure_17/generate_supp_figure_17.py
python Supp_Figure_19/generate_supp_figure_19.py
python Supp_Figure_25/generate_supp_figure_25.py
python Supp_Figure_26/generate_supp_figure_26.py
```

## Folder-to-Output Mapping

- `Main_Figure_4_lower`: `main_figure_4_lower.png`, `main_figure_4_lower.pdf`
- `Main_Figure_6_upper`: `main_figure_6_upper.png`, `main_figure_6_upper.pdf`
- `Main_Figure_7_lower`: `main_figure_7_lower.png`, `main_figure_7_lower.pdf`
- `Main_Figure_8`: `main_figure_8_a.png`, `main_figure_8_a.pdf`, `main_figure_8_b.png`, `main_figure_8_b.pdf`
- `Supp_Figure_17`: `supp_figure_17_a.png`, `supp_figure_17_b.png`, `supp_figure_17_c.png`
- `Supp_Figure_19`: `supp_figure_19.png`, `supp_figure_19.pdf`
- `Supp_Figure_25`: `supp_figure_25.pdf`
- `Supp_Figure_26`: `supp_figure_26.pdf`

All outputs are written to the same directory as the corresponding script file.

## Python Script Naming Style

Current `.py` naming statistics:

- Total scripts: `8`
- `snake_case`: `8/8` (100%)
- Prefix distribution: `generate_*` = `8`

Naming style is consistent and follows lowercase `snake_case` across all plotting scripts.

## Notes

- Scripts are self-contained and use embedded data.
- Generated files are saved in the corresponding script directory.
