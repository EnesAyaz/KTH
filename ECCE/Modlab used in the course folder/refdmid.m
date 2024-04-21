function refout = refdmid(ref1,ref2,ref3)
%Zero-sequence for discontiuous modulation, mid(ref(i)) clamped
%
% Zero-sequence for discontiuous modulation with clamping of the reference
% curve with intermediate instantaneous magnitude. This implies that the
% phase with the instantaneous reference
%
n=length(ref1);
%
ref=[ref1;ref2;ref3];
%
[refsort,i_ref] = sort(abs(ref));
%
%refmid=ref(i_ref(2,:)');
%
for count=1:n
 refmid(count)=ref(i_ref(2,count),count);
end;
%
refout= sign(refmid+eps)-refmid;       % zero-sequence
