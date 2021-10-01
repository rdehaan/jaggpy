% ASP Solver practice file
% Code based on Paper by de Haan and Slavkovik

% Declare voters and issues (now only literals)
voter(1..17).
issue(i1;i2;i3;i4;i5).

% Declare variables
variable(i1;i2;i3;i4;i5;i6).
1 {js(cons, X); js(cons, -X)} 1 :- variable(X).

:- inputClause(C,_), js(cons,-L) : inputClause(C,L).
:- outputClause(C,_), js(cons,-L) : outputClause(C,L).

consistency(X) :- js(cons, X).

% Declare input constraints (in CNF)
inputClause(1, (i3;-i4)). 
inputClause(2, (-i1;-i3;i4)).
inputClause(3, (-i2;-i3;i4)).
inputClause(4, i6).

% Declare ouptut constraints (in CNF)
outputClause(1, (i3;-i4)). 
outputClause(2, (-i1;-i3;i4)).
outputClause(3, (-i2;-i3;i4)).
outputClause(4, i6).

% Consistency check with respect to the input constraint
agent(A) :- voter(A).
lit(X;-X) :- issue(X).
1 { js(A,X) ; js(A,-X) } 1 :- agent(A), issue(X).
:- voter(A), inputClause(C,_), js(A,-L) : inputClause(C,L).

% Consistency check of the collective outcome with respect 
% to the output constraint
agent(col).
:- agent(col), outputClause(C,_), js(col,-L) : outputClause(C,L).

% Encode the profile, this also needs to include the negation
% of the formulas that are not accepted. 
js(1..6, (i1;i2;i3;i4;i5)).
js(7..10, (i1;i2;-i3;-i4;i5)).
js(11..17, (-i1;-i2;i3;-i4;-i5)).

% Kemeny rule 
wgt(X,N) :- lit(X), N = #count { A : voter(A), js(A,X) }.
#maximize { N@1,wgt(X,N) : wgt(X,N), js(col,X) }.

% % Leximax rule
% wgt(X,N) :- lit(X), N = #count { A : voter(A), js(A,X) }.
% #maximize { 1@N,wgt(X,N) : wgt(X,N), js(col,X) }.

% Young rule
% in(A) ; out(A) :- voter(A).
% inwgt(X,N) :- lit(X), N = #count{ A : voter(A), in(A), js(A,X) }.
% inmaj(X) :- lit(X), inwgt(X,N), inwgt(-X,M), N > M.
% js(col,X) :- inmaj(X).
% #minimize { 1@1,out(A) : out(A) }.

% Reversal scoring
% agent(vrt(A,X)) :- voter(A), lit(X). 
% js(vrt(A,X),-X) :- voter(A), lit(X), js(A,X).

% disagree(A,X,Y) :- voter(A), lit(X), lit(Y), js(A,Y), js(vrt(A,X),-Y).
% disagreement(A,X,D) :- voter(A), lit(X), D = #count { Y : disagree(A,X,Y) }.
% #minimize { D@2,disagreemt(A,X,D) : disagreement(A,X,D) }.

% score(A,X,D) :- js(col,X), disagreement(A,X,D).
% score(E) :- E = #sum { D,score(A,X,D) : score(A,X,D) }.
% #maximize { E@1,score(E) : score(E) }.

% % Slater rule
% % determine the majority outcome
% pc(X,N) :- lit(X), N = #count { A : voter(A), js(A,X) }.
% maj(X) :- lit(X), pc(X,N), pc(-X,M), N > M.
% % maximize agreement with the majority outcome
% #minimize { 1@10,maj(X) : maj(X), js(col,-X) }.

% % Majority rule
% % require that the collective outcome agrees with all issues
% % that have strictly more support than their negation
% pc(X,N) :- lit(X), N = #count { A : voter(A), js(A,X) }.
% maj(X) :- lit(X), pc(X,N), pc(-X,M), N > M.
% js(col,X) :- maj(X).

% Represent the outcome 
outcome(X) :- agent(col), js(col, X).

% #show consistency/1.
#show outcome/1.