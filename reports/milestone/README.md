# Milestone report

- **[milestone_report.pdf](milestone_report.pdf): three content pages plus one references-only page.**
- `milestone_report.tex`: editable report source.
- `metrics_table.tex`: result table calculated from recorded per-seed metrics.
- `neurips_2026.sty`: unmodified official NeurIPS 2026 style.
- `template_provenance.json`: official author-kit URL and hashes.
- `validation.json`: page-count, source/style, and content checks.

This is a CS 4824 milestone report using the official template's **preprint** option, not a claim of submission to or acceptance at NeurIPS. The course's three-content-page limit controls; only references occupy page 4. No appendix is placed outside that limit.

The current team and Contributions section are Trisha Bajpai, Basmala Metwally, and Jacob Loe. Jacob confirmed the completed roles and took over ingestion/documentation work following the team change. AI assistance is disclosed. Team review of the final report remains necessary.

## Build locally

With a TeX distribution installed, run from this folder:

```bash
pdflatex -interaction=nonstopmode -halt-on-error milestone_report.tex
pdflatex -interaction=nonstopmode -halt-on-error milestone_report.tex
```

No BibTeX step is needed: bibliography entries are in the source. The style and table are local; no external figure files are required. Standard TeX packages include `natbib`, `environ`, `geometry`, `fontenc`, `booktabs`, `tabularx`, `amsmath`, `hyperref`, and Latin Modern typewriter fonts (`lm`); Times body fonts are selected by the official style.

## Edit in Overleaf

Upload `milestone_report.tex`, `metrics_table.tex`, and `neurips_2026.sty` to a project and set `milestone_report.tex` as the main document. Recompile and recheck the page count after edits. Keep the official margins and body font sizes; shorten the prose instead of shrinking the format.

The thesis, survey case/matrix, completion plan, and confirmed contribution record also appear in `../../docs/`. Experimental files remain unchanged. The main repository is private, so instructor access must be arranged for the report's code link.
