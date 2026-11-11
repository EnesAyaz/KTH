# Official template execution contract

Reference: template/ICPE_2027_Digest_Template.docx, downloaded 2026-11-09 from https://www.icpe-conf.org/main/filedownload.htm?type=link&uid=25 . Reference renders: qa/template_reference-1.png through -3.png. Reference retained unchanged; SHA-256 and package inventory are in template_inventory.json.

Three reference pages: two illustrative digest pages and one author-guideline page. Two section patterns, both A4, 3 cm top, 2.5 cm bottom; the stored 1.651 cm side margins conflict with written 2.5 cm requirement. Final explicitly follows written 2.5 cm side margins. Single column. Footer uses centered PAGE field at about 0.76 cm from bottom. No author block.

Typography: Times New Roman; original body 11 pt, Text style justified with first-line indent about 0.356 cm and 1.05 line spacing. Heading 1 centered 12 pt bold small caps with Roman numbering; heading 2 12 pt bold italic. Title 16 pt bold centered. Caption centered, regular. Title will use Word Title style; remove floating title frames to permit normal content flow. Use black throughout text; restrained colour appears only in plots. Tables are new comparable-data elements with 10 pt type, visible light-gray borders and light-gray header fill.

Editable slot: word/document.xml body example content and guideline section are replaced by the five-page paper; clone source paragraph roles, with explicit page breaks between planned pages. Preserve final section footer relationship, paper size and footer. Remove guideline-only section break as intentionally unused. Body equations will be native Word math. New images are original plots; no template sample diagram is reused in the paper. No controls or metadata from the author-guideline text are carried into body content.

Preserve all source package parts byte-for-byte except document.xml, document.xml.rels, styles.xml (Title role), settings.xml (updateFields), [Content_Types].xml (new PNGs), and core.xml (anonymous metadata). New media parts may be added. Existing unused sample-media parts may remain preserved. All other original relationships, footer and numbering/styles remain unchanged. A package audit verifies this after authoring. Reference is never overwritten.

Rendering: packaged render_docx.py was attempted and failed because no LibreOffice executable exists. Microsoft Word COM successfully exported the template to PDF, followed by bundled Poppler rasterization. Use the same native Word rendering fallback for final QA; do not use installed LibreOffice. Preserve the DOCX without a Word save during render; update fields in memory only. Inspect every final page.


IEEE editorial revision: single-column five-page digest, 10-pt main text, numbered native equations, centered captions and tables, horizontal table rules, and four consistent technical figures. Official reference package preserved except documented body/style/metadata parts.
