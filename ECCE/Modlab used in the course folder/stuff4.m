function n = stuff4(d, noofpts);
%Creates sampled switching functions during one switching cycle
%
% n = stuff(d, noofpts)
%
% noofpts: (integer)
% d: (real vector with four elements) sum(d)=1
% n: (integer vector with four elements)
%
n1=noofpts*d;
n=round(n1);
nrest=n1-n;
sum1=round(sum(nrest));         % -2, -1, 0, 1 or 2
[dummy,ind]=sort(abs(nrest));   % Order the elements by rounding error
ind = ind(4:-1:1);              % Reorder to descending order
for rakn = 1:abs(sum1),
    n(ind(rakn)) = n(ind(rakn)) + sign(sum1);   % Adjust the elements with max rounding error
end;
if (sum(n)~=noofpts) error('Wrong number'); end;
