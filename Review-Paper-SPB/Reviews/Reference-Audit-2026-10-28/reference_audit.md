# Reference audit — 28 October 2026

Scope: all 122 numbered references in the current compiled bibliography. The BibTeX database has 182 records (including a formatting-control record); uncited records are outside this published-bibliography audit. No manuscript, figure, bibliography, or PDF was changed.

## Assessment

No confirmed fabricated reference was identified. All 105 entries that already contain a DOI resolve to matching paper titles (104 distinct DOI strings because [32]/[78] duplicate one paper). The remaining 17 entries were checked through manufacturer, publisher, standards-body, or institutional sources; the missing DOI for [42] was also recovered. Source identity is not a guarantee that every claim citing it is supported. This audit checks bibliographic identity and metadata, rendered style, and the vehicle/manufacturer claims in Table 1; it is not a full-text technical validation of every cited assertion.

The main concerns are an incorrect author list, duplicate records, incomplete metadata, publication-status ambiguity, capitalization, and inconsistent web citations. Reference [26] has a conflicting author list across metadata sources and needs a first-page check; do not automatically overwrite its authors from the registry.

## Corrections before submission

| Reference | Finding and proposed correction |
|---|---|
| [40] | **Incorrect authors.** Replace `Wang, Li and Han, Yehui` with Jiyao Wang, Ye Li, and Yehui Han. [Registered DOI record](https://doi.org/10.1109/TIA.2015.2413380). |
| [32], [78] | **Same paper cited twice under different keys.** Consolidate to one record while retaining both citation locations. DOI 10.1109/JESTPE.2023.3283538. |
| [49] | **Publication status is not established.** KTH labels the record submitted; the downloadable manuscript is real. Cite it as a submitted manuscript/preprint unless a final journal record can be supplied. Remove the editorial note “published-version DOI not located.” [KTH record](https://kth.diva-portal.org/smash/person.jsf?pid=authority-person%3A32580). |
| [65] | Replace `pp. 1–1` with the current registered details: vol. 12, no. 5, pp. 8369–8383, Oct. 2026. [DOI](https://doi.org/10.1109/TTE.2026.3697111). |
| [2], [3], [58] | Article numbers 3063, 384, and 1259 are present in BibTeX as `ARTICLE-NUMBER`, but the current style omits them. Use a supported representation that prints “Art. no.” correctly. |
| [74] | Add pp. 3900–3905. [Publisher](https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/joe.2018.8258). |
| [94], [96] | Add pp. 1–6 and pp. 1–4, respectively. |
| [110] | Add vol. 52, no. 4, pp. 3124–3132. The DOI metadata is stale, so use the final institutional record. [Nottingham](https://nottingham-repository.worktribe.com/output/800775/a-modular-speed-drooped-system-for-high-reliability-integrated-modular-motor-drives). |
| [42] | Add the verified missing DOI: 10.1109/COBEP.2015.7420104. |
| [83] | Print the standard identifier **IEC 60664-1:2020** explicitly; the current `@manual` formatting loses its `number` field. If citing the consolidated amendment, identify IEC 60664-1:2020+AMD1:2025 CSV. [IEC](https://webstore.iec.ch/en/publication/59671). |
| [7], [8], [122] | Add retrievable URLs; these cited product/website/datasheet entries currently have none. The EPC2361 datasheet revision dated July 20, 2026 is genuine. |
| [26] | Registered metadata lists Nehmer, Bakran, Hepp, while the manuscript lists Nehmer, Hepp, Wondrak, Bakran. Title/DOI are genuine, but full authors and ordering remain unresolved; inspect the paper first page. |

## Websites and production vehicles

Manufacturer sources are appropriate for product specifications and production-vehicle examples. They are not peer-reviewed evidence of comparative scientific superiority. Keep them as industrial context and cite the exact document/page, model year, trim, and operating condition. IEEE explicitly provides an online-reference format with corporate author, page title, access date, and URL. [IEEE Reference Guide](https://journals.ieeeauthorcenter.ieee.org/wp-content/uploads/sites/7/IEEE_Reference_Guide.pdf).

Table 1 currently mixes architectural voltage classes, nominal battery voltages, converter output ratings, combined vehicle motor power, and short-duration boost power. Its values should be labelled as such rather than presented as directly comparable continuous inverter ratings.

| Entry | Verified assessment |
|---|---|
| Bosch Gen. 4 [7] | Manufacturer confirms 400/800-V classes, up to 250/350-kW **peak** power. Add URL and peak qualifier. |
| BMW i4 M50 [8] | Real vehicle; BMW documentation supports 398.5-V battery and 400-kW combined maximum power. Prefer BMW’s primary source over an unlinked ADAC title. State model year and maximum/boost condition. |
| TI/Wolfspeed [10] | Real 800-V, 300-kW reference design. It is jointly developed by TI and Wolfspeed; label accordingly. Do not treat an access year as its publication year: TI documents existed in 2023–2025. |
| Hyundai IONIQ 5 N [11] | 478 kW is a **10-second N Grin Boost** value; standard maximum is 448 kW. Manufacturer lists nominal battery voltage 697 V, despite the 800-V architecture class. [Hyundai specifications](https://www.hyundaiusa.com/us/en/vehicles/ioniq-5-n/compare-specs). |
| Infineon eCAV [13] | 800 V / 250 kW confirmed. This reference platform uses IGBT7 modules, not SiC. User guide is dated Sept. 30, 2024; the current 2026 bibliography year is not established as a publication date. [Product page](https://www.infineon.com/evaluation-board/REF-CAV250KMT7INV). |
| Volvo EX90 [14] | 800-V architecture and 500-kW Twin Motor Performance rating are supported for the updated MY2026 vehicle; identify the model year because earlier versions differ. Current US page has an apparent kWh/kW typography error; prefer a dated technical specification. |
| AVL PI850e [16] | 800 V / up to 250 kW supported. It is an A-sample development platform, not evidence of a production vehicle. The table already separates industrial/reference platforms; retain that distinction. |
| Porsche Taycan Turbo S [17] | 700 kW is **overboost with Launch Control**; technical sheet separately lists 570 kW. Specify condition and model year. [Manufacturer page](https://www.porsche.com/international/models/taycan/taycan-models/taycan-turbo-s/). |
| Punch IV5 [19] | Current manufacturer product page supports up to 600 kW. Older 2025 launch material says over 400 kW; retain an exact dated source or archived snapshot for the 600-kW claim. |
| Lucid Dream Edition P [20] | The 2022 European announcement supports 828-kW combined motor power. Replace the abbreviated invented page label with the actual release title. The 900-V-plus architecture needs its own supporting specification if not stated in that release. [Original release](https://ir.lucidmotors.com/news-releases/news-release-details/lucid-motors-announces-launch-plans-europe-pricing-and-specs). |

## Consistent IEEE presentation

- Protect technical capitalization in BibTeX titles: `{GaN}`, `{SiC}`, `{SPB}`, `{PWM}`, `{EMI}`, `{PMSM}`, `{BMW}`, `{IPM}`, `{DC}`, `{kV}`, `{MW}`, `{kW}`, and `{V}`. Current output includes forms such as “gan”, “sic”, “pwm”, “2-kv 1-mw”, and “250 kw”; sentence case does not justify corrupting acronyms or unit symbols.
- Use exact source titles, verified publication dates, and `Accessed: Oct. 28, 2026` only for pages checked on that date. Existing August access dates cannot be independently substantiated by this audit. Do not equate access year, vehicle model year, and page publication year.
- Do not bury performance claims in the bibliography’s note fields. Put conditions in Table 1 or its footnote and keep source entries bibliographic.
- The current bibliography style does not print most DOI fields. Adding DOI output would improve traceability; absence of a printed DOI alone does not prove a reference is invalid.
- Use early-access formatting plus DOI for genuinely unassigned articles, rather than a placeholder `pp. 1–1`. Check [88] again at submission.
- Retain the author-name preference (no repeated-author dash).
- Automated registry differences are not automatically errors. For example [33] has incomplete registry author metadata, but the publisher PDF confirms Thomas M. Jahns and Hang Dai; keep the current authors. Some conference metadata also omit page ranges even when local values are legitimate.

## Verification ledger

See `reference_checklist.csv` for all 122 numbered entries, verification links, and individual notes. The saved registry metadata in `verified_doi_metadata.json` provide a reproducible snapshot. Counts refer to bibliography entries, not unique scientific works.
