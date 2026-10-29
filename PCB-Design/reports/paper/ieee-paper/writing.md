# Text, tables and results

## 1. Tables carry the numbers, the text carries the meaning

A value that is printed in a table is not repeated in the text. The reader can read the table. The text refers to it and says what the numbers mean: which case is larger, why, and what follows from it.

- **Parameters.** Ratings and the parameters of the machine, the converter and the setup go into a table. They are not listed again in a sentence.
- **Allowed in the text.** The one or two numbers on which an argument turns, such as a headline result or a limit from a datasheet. Each appears once.
- **Same value everywhere.** A quantity has one value in the abstract, the text, the tables and the conclusion.

Not this:

> Method A has a loss of 12.4 W, a ripple of 16.1 V and a common-mode voltage of 133 V, while method B has a loss of 10.9 W, a ripple of 32.9 V and a common-mode voltage of 96 V.

But this:

> Table III compares the two methods. Method B has the lower loss, because it never commutates through a zero vector, and pays for it with twice the ripple.

For the table itself:

- One quantity per column, with the unit in the header.
- The same number of significant digits within a column, normally three.
- Rows in the same order as in the figures and the text.
- One column wide if it fits.
- No vertical rules.

## 2. Small numerical differences

A difference of one or two percent between two cases in a simulation or a numerical calculation is usually no difference at all. The two quantities are identical analytically and the numerics make them look different. Such differences are not carried into the paper.

1. **Ask what theory says before printing two close numbers.** Derive the quantity, or find the symmetry argument. Example: two modulation sequences that commutate through the same three line voltages equally often have exactly the same mean commutation voltage, whatever the simulation prints.
2. **If they are equal in theory, print one value for both.** Use the closed form where there is one, otherwise the common rounded value. State that they are equal. Do not write "within 2 %", "almost the same" or "slightly higher". Do not print a column that reads 1.00, 1.01, 1.01.
3. **A small difference is real only if it has a reason.** The reason can be stated in one sentence, and the difference remains with ideal inputs and finer numerics. Then report it with the reason. Tell the author explicitly that this one is real, because they will assume it is numerical.
4. **Derived columns are consistent.** Ratios and percentages are computed so that equal inputs give exactly equal results.
5. **Digits.** Print no more digits than the method supports. A digit that changes with the time step is noise.

The usual causes of such differences:

- The time step and the solver tolerance.
- An averaging window that is not a whole number of periods, or that includes the start-up transient.
- Quantities sampled at discrete instants or angles.
- Runs made with different step or sampling settings.
- Events that fall on the edge of the evaluation window.
- Intermediate values that were rounded.

## 3. Abbreviations

1. **Define at first use.** Write the term out and put the abbreviation in parentheses: "current source inverter (CSI)". From then on use only the abbreviation. Do not spell it out again and do not define it twice.
2. **Never before the definition.** An abbreviation does not appear in the text, a heading, a caption, a table or a figure before the sentence that defines it. This is the rule that gets broken when sentences or sections are moved, so recheck the first use after every reordering.
3. **Abstract and body are separate.** Define the abbreviation in the abstract, and define it again at its first use in the body. This is the IEEE rule.
4. **Title.** No abbreviations in the title unless they are universally known.
5. **Figures and tables.** An abbreviation used in a figure, a legend or a table header is defined in that caption or earlier in the text.
6. **Only what is used.** A term used fewer than three times is written out. Do not coin abbreviations to save space. Too many make the text unreadable.
7. **Names of new methods.** A method the paper introduces gets its full name and its abbreviation in the sentence that introduces it.
8. **No definition needed.** SI units, IEEE, and ac, dc and rms. Keep one capitalisation of these throughout the paper.
9. **Form.** The plural takes an "s" without an apostrophe. The article follows the pronunciation: "an FSM", "a CSI".

To check: list every abbreviation in the paper, find its first occurrence, and confirm that this occurrence is the definition. Do it separately for the abstract and for the body, and include captions and headings.

## 4. Cross-references

1. **Every figure and every table is referred to in the text**, by its number, at least once. A figure or table that no sentence refers to either gets a sentence or is removed.
2. **The reference says what to look at.** "Fig. 4 shows that the switch stays off for one sector" is a reference. "(see Fig. 4)" at the end of a sentence is not enough.
3. **Order.** The first references appear in numerical order: Fig. 1 is mentioned before Fig. 2.
4. **Distance.** A figure or table sits close to its first reference, ideally on the same page or the next one. They are never more than two pages apart, in either direction, unless the author says otherwise.
5. **Fixing the distance.** Move the float in the source to the paragraph of its first reference. Put a two-column float about one page earlier in the source. Or move the sentence. Do not force the position with `[h!]` or `[H]`.
6. **Recheck after every change that moves text.** Floats shift when text is added or removed. After compiling, compare the page of each float with the page of its first reference. The `.aux` file holds the page of every label.
7. **Form.** "Fig. 3", "Figs. 3 and 4", "Table II", equation "(5)", "Section III-B". Use a non-breaking space before the number. No "??" may remain in the output.
8. **Same names as in the figure.** The text refers to parts of a figure by the labels and legend entries that are visible in it.

## 5. Scope

- **Do what was asked.** Do not add analyses, metrics, figures, derivations or sections that were not requested. Mention the idea in the reply and add it only when the author agrees.
- **Removed means removed.** What the author took out does not come back in a later version, in another section or in another wording.
- **Show first.** When the author asks to see something before it goes into the paper, it stays out of the paper until they approve it.
- **Page limit.** Respect it, but do not cut content to meet it unless asked. Say that the paper is over the limit and by how much.

## 6. Language and terms

- **Plain language.** Short declarative sentences, common words, one idea per sentence.
- **No filler.** No sentence that only announces what comes next. No sentence that repeats a caption. No "it is worth noting that" and no "as can be clearly seen".
- **The established term of the field.** Use the term the cited literature uses, and check its exact meaning first. Sampling period and switching period, for example, are different things. Do not coin a name for a concept that already has one.
- **One term for one thing.** Once a term is chosen, it is used everywhere: text, figures, tables, captions.
- **Name things by their label.** "Sector 1", "S1", "Fig. 2(b)", with a diagram that defines the labels. Not a description such as "the sector around the crest of the current".
- **Symbols.** Each symbol is defined at first use and is the same in text, equations, figures and tables.
- **No working names.** Names of scripts, internal models and helper tools from the work do not appear in the paper. Say where a number comes from in the reader's terms: simulation, measurement or analysis.
- **Source of results.** Results come from the source the paper names. A helper calculation is not presented as a simulation result.
- **Equal basis.** Alternatives are compared on an equal, stated basis. Methods that switch a different number of times per sampling period, for example, are compared at the same number of switching events per second.
- **Introduce before use.** A method, a quantity or a figure element is explained before the text relies on it.
- **Sources.** Cite what the author supplies. Refer to a commercial part through its datasheet citation and do not describe the product in the text more than the argument needs.
