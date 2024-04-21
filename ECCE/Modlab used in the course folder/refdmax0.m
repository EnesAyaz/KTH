function ref = refdmax0(ref1,ref2,ref3)
%Zero-sequence for discontiuous modulation, max(ref(i)) clamped
%
% Zero-sequence for discontiuous modulation with clamping of the reference
% curve with highest magnitude
%
refmin=min([ref1; ref2; ref3]);
refmax=max([ref1; ref2; ref3]);
mm=abs(refmax)>abs(refmin);
ref= mm.*(1-refmax) + (mm-1).*(1+refmin);    % zero-sequence
