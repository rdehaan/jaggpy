% ASP Solver practice file
% Code based on Paper by de Haan and Slavkovik

% Declare voters and issues (now only literals)
voter(1..11).
issue(x1;x2;x3;x4).

% Declare input constraints (in CNF)
inputClause(1,(-x1;-x2;-x3)). 
inputClause(2, (-x1;-x3;-x4)).

% Declare ouptut constraints (in CNF)
outputClause(1, (-x1;-x2;-x3)). 
outputClause(2, (-x1;-x3;-x4)).

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
js(1..4, (x1;-x2;x3;-x4)).
js(5..7, (-x1;x2;x3;x4)).
js(8..10, (x1;x2;-x3;x4)).
js(11, (x1;x2;-x3;-x4)).

% % Kemeny rule 
% wgt(X,N) :- lit(X), N = #count { A : voter(A), js(A,X) }.
% #maximize { N@1,wgt(X,N) : wgt(X,N), js(col,X) }.

% % Leximax rule
% wgt(X,N) :- lit(X), N = #count { A : voter(A), js(A,X) }.
% #maximize { 1@N,wgt(X,N) : wgt(X,N), js(col,X) }.

% Young rule
% in(A) ; out(A) :- voter(A).
% inwgt(X,N) :- lit(X), N = #count{ A : voter(A), in(A), js(A,X) }.
% inmaj(X) :- lit(X), inwgt(X,N), inwgt(-X,M), N > M.
% js(col,X) :- inmaj(X).
% #minimize { 1@1,out(A) : out(A) }.

% Represent the outcome 
outcome(X) :- agent(col), js(col, X).

#show outcome/1.