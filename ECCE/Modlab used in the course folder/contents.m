% Power converter modulation toolbox
%
% Staffan Norrga 2004-2005
%
% KEY TO NAMES: 
% Functions with names mod_xxxxx.m generate a sampled version of a certain
% modulation form during a carrier cycle
% 
% Functions with names anaxxxxx.m analytically compute the harmonic spectrum of a certain modulation form using a double Fourier series
% approach
%
% GENERAL
% anaspect2lnsc - Analytically computes the spectrum of naturally sampled constrained modulation of a phase leg (uses sband1plja.m) 
% carrsawc      - Alternating sawtooth carriers
% carrsawn      - Sawtooth carrier with falling flanks
% carrsawp      - Sawtooth carrier with rising flanks
% carrtri       - Triangular carrier
% fourcoef      - Numerical calculation of Fourier coefficient by evaluation of the Fourier integral
% fourser       - Fourier series expansion by fft algorithm
% mod_2lcarr    - Two-level carrier-based PWM modulation of a single phase leg
% mod_nspwm     - Two-level naturally sampled PWM modulation of a single phase leg (M=1 -> U1=1)
% mod_nspwmc    - Two-level constrained naturally sampled PWM modulation of a single phase leg (M=1 -> U1=1)
% regsamp       - Generates regularly sampled cosine waveform
% sband1plja    - Analytic calculation of sideband harmonics for a single phase leg with constrained modulation 
% spect2lanalyt - Analytic spectra of 2-level unconstrained modulation with natural sampling. (M=1 -> U1=1)
% stuff         - Creates sampled switching functions during one switching cycle, 3 vectors
% stuff4        - Creates sampled switching functions during one switching cycle, 4 vectors
% thd           - THD calculation (removed)
% wthd          - Weighted THD calculation (removed)
%
%
% SINGLE_PHASE SYSTEMS
% anaspect1ph3lnsc  - Analytically computes the spectrum of 3-level single phase naturally sampled constrained modulation (uses sband1pja.m)
% mod_1phnspwmc     - Three-level single phase constrained naturally sampled PWM modulation (M=1 -> U1=2)
% mod_1phrspwmc     - Three-level single-phase constrained regularly sampled PWM modulation (M=1 -> U1=2)
% sband1pja:        - Analytical calculation of sideband harmonics using the Jacobi-Anger expansion, single-phase three level modulation
%
%
% THREE_PHASE SYSTEMS
% abc2alfabeta   - abc -> alfabeta conversion for three-phase system on phasor form
% cursqavg       - Computes the average of the square of the normalised ripple current during a fundamental cycle
% evalpwm        - Extracts certain parameters from a 3-phase pwm pattern
% itr_rms        - Computes the ratio of the transformer rms current to the phase rms current
% mod_pwm        - Two-level three-phase regularly sampled PWM modulation (M=1 -> U1=1) (removed)
% mod_pwmc       - Two-level three-phase constrained regularly sampled PWM modulation (M=1 -> U1=1)
% mod_svm        - Two-level SVM modulation (M=1 -> U1=1)
% mod_svmc       - Two-level constrained SVM modulation (M=1 -> U1=1)
% mod_svmc_mirp2 - Two-level constrained SVM modulation (M=1 -> U1=1), can use 4-vector sequences
% pn0            - abc -> pn0 conversion
% pwmfplot       - Plots switching functions for 3-phase system in the frequency domain
% pwmplot        - Plots phase and line-to-line switching functions for 3-phase system
% refdmax0       - Zero-sequence for discontiuous modulation, max(ref(i)) clamped
% refdmid        - Zero-sequence for discontiuous modulation, mid(ref(i)) clamped
% rmmid          - Conversion phase potentials -> phase-to-load-midpoint voltages
% rmmid2         - Conversion phase potentials -> phase-to-load-midpoint voltages (vector input)
% svm            - Two-level SVM modulator
% svmc           - Two-level constrained SVM modulator
% svmc_mirp2     - Two-level constrained SVM modulator type 2
% svmc_mirp3     - Two-level constrained SVM modulator type 3
% svmc_mirp4     - Two-level constrained SVM modulator type 4
%
%
% TWO-LEVEL HARMONIC ELIMINATION
% harmelim.m        - 2-level harm elimination quarter-wave and half-wave symmetry, solves for angles (removed)   
% timeq.m           - 2-level harm elimination quarter-wave and half-wave symmetry, computes time function from angles
% harmelimdemo.m    - 2-level harm elimination quarter-wave and half-wave symmetry, DEMO (removed)
% hefindsol.m       - Script that tries to find all solutions, extends them and plots them (removed)
%
%
% THREE-LEVEL HARMONIC ELIMINATION
% harmelim3l.m      - 3-level harm elimination quarter-wave and half-wave symmetry, solvs for angles (removed)
% threeltfcn.m      - 3-level harm elimination quarter-wave and half-wave symmetry, computes time function from angles
% he3ldemo.m        - 3-level harm elimination DEMO (removed)
%
%
% MULTI-LEVEL HARMONIC ELIMINATION BLOCK MODULATION
% harmelimblock.m   - Multilevel block modulation, solvs for angles (removed)
% mlblock.m         - Multilevel block modulation time function (removed)
% MLblockdemo.m     - Multilevel block modulation DEMO (removed)
%
%
% MISCELLANEOUS
% Notchmoddemo.m    - Notch modulation cf. fig 2.5 in Holmes.





