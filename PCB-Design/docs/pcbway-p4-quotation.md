# P4 fabrication and assembly quotation requirements

Initial supplier reference: PCBWay; a European supplier may use the same requirements. No files have been uploaded and no supplier has been contacted.

Request a four-layer 78.5 × 51 mm board, nominal 1.6 mm copper/laminate thickness, with 70 µm finished outer and 35 µm inner copper. The requested finished outer dielectric spacing is 0.100 mm on both sides. Obtain a named stackup and tolerances; update the geometry and inductance estimate if the supplier substitutes a different spacing.

Current minimum route width is 0.15 mm, with 0.20 mm general clearance. Through vias are nominal 0.30 mm drill / 0.60 mm pad. Check the copper-weight-specific etching limits and finished-hole convention, including connector hole tolerance. The generic pin-header footprint currently uses 1.0 mm drills; compare against the configured Samtec land pattern before purchasing.

PCBWay publishes copper and drill options on its [manufacturing tolerances page](https://www.pcbway.com/pcb_prototype/PCB_Manufacturing_tolerances.html) and provides separate [copper-weight-specific trace/space guidance](https://www.pcbway.com/helpcenter/ordering_parameter_instruction/What_is_the_Min_Track_Spacing_for_1oz__2oz__3oz__Copper_weight_.html). These general capabilities do not establish acceptance of this particular 2 oz fine-pitch layout.

Use the current [stackup selection guidance](https://www.pcbway.com/blog/12/How_to_Choose_the_Stackup_for_Your_Needs_efcad645.html), not an old fixed stackup image. Exact 0.100 mm/2 oz availability remains unconfirmed.

Request a reviewed paste-volume strategy for EPC lands and the split-exposed-pad LMG1210. P4 replaces the large THR terminals with headers, which changes the assembly process from P3. PCBWay offers [stepped stencils](https://www.pcbway.com/blog/13/Get_to_know_the_Multi_level__Step_Stencil.html) and multiple [stencil thickness options](https://www.pcbway.com/stencil.aspx); the assembler must select the actual process. Surface finish, header insertion/soldering method and component polarity inspection remain to be specified.

The board is for engineering review. Cold-plate and support mechanics, connector loading, collector current density and switching behavior remain unqualified. A clean DRC report does not resolve those release items.
