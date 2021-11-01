# JAGGPY

`jaggpy` is a Python package for computing outcomes of [judgment aggregation](https://plato.stanford.edu/entries/belief-merging/#JudAgg) (JA) scenarios. The package allows for JA scenarios in the most general form, where issues in the agenda, constraints on judgment sets and constraints on the outcome may be arbitrary formulas. For more information on the formal framework used see, e.g.,
> Endriss, U., de Haan, R., Lang, J., & Slavkovik, M. (2020). [The Complexity Landscape of Outcome Determination in Judgment Aggregation](https://doi.org/10.1613/jair.1.11970). *Journal of Artificial Intelligence Research*, *69*, 687-731.

in which it is referred to as *framework (6)*.

The package offers two ways in which to generate outcomes for a scenario given a JA rule. The first (and slowest) is a brute force solver, and the second makes use of Answer Set Programming (ASP) for the efficient computation of outcomes, building on the encodings presented by de Haan and Slavkovik in

> de Haan, R., & Slavkovik, M. (2019). [Answer set programming for judgment aggregation](https://doi.org/10.24963/ijcai.2019/231). In *Proceedings of the 28th International Joint Conference on Artificial Intelligence (IJCAI 2019)*. AAAI Press.

<!-- TABLE OF CONTENTS -->
## Table of contents
<ol>
<li>
    <a href="#getting-started">Getting started</a>
    <ul>
    <li><a href="#prerequisites">Prerequisites</a></li>
    <li><a href="#installation">Installation</a></li>
    <li><a href="#tests">Tests</a></li>
    </ul>
</li>
<li>
    <a href="#usage">Usage</a>
    <ul>
    <li>
    	<a href="#scenario-objects">Scenario objects</a>
	<ul>
	<li><a href="#formulas">Formulas</a></li>
	<li><a href="#jagg-file">.jagg file</a></li>
	<li><a href="#creating-a-scenario-object">Creating a Scenario Object</a></li>
	<li><a href="#scenario-methods-and-properties">Scenario methods and properties</a></li>
	</ul>
    </li>
    <li>
        <a href="#using-the-solver">Using the solver</a>
        <ul>
        <li><a href="#creating-a-solver-object">Creating a solver object</a></li>
        <li><a href="#solver-methods">Solver methods</a></li>
        </ul>
    </li>
    <!--<li><a href="#examples">Examples</a></li>-->
    </ul>
</li>
<li><a href="#license">License</a></li>
<li><a href="#acknowledgements">Acknowledgements</a></li>
<li><a href="#contact">Contact</a></li>
<li><a href="#references">References</a></li>
</ol>

<!-- GETTING STARTED -->
<!-- This still needs to be done! -->
## Getting Started
### Prerequisites
At least Python 3.4 is required.

### Installation
To install the package run the following command
```
pip install jaggpy
```

This will automatically install (if not yet available)
the following dependencies:
- [nnf](https://pypi.org/project/nnf/)
- [pyparsing](https://pypi.org/project/pyparsing/)

Part of the functionality of `jaggpy` depends
on [clingo](https://potassco.org/clingo/),
which is most conveniently installed using [Anaconda](https://conda.io),
e.g., with:
```
conda install -c potassco clingo
```


### Tests
To check whether the package and all dependencies are installed and working properly, run the following command:
```
python -m unittest jaggpy.tests
```

<!-- USAGE -->
## Usage
To use this package you need to create a scenario object for the scenario that you want to apply judgment aggregation to. Futhermore, a solver object needs to be made to apply one of the aggregation rules to the scenario. These objects and their methods will be discussed in the following.

<!-- Scenario objects -->
### Scenario objects

#### **Formulas**

This package can handle arbitrary formulas in the agenda, input-, and output constraints. The available operators are conjunction (`&`), disjunction (`|`), negation (`~`) and implication (`->`). Parentheses can usually be omitted where clear from context. A few example formulas are:
```
 (~x1 | ~x2 | ~x3) & (~x1 | ~x3 | ~x4)

 (x1 -> ~(x2 & x3)) & (x1 -> ~(x3 & x4)))

 ( ~x1 & x2 ) -> x3
```
#### **`.jagg` file**
An object from the scenario class is read from a `.jagg` file. A `.jagg` file should be formatted as follows:

- `var_1,...,var_n`: A list of all the variables occuring in the scenario.
- `m`: The number of issues in the pre-agenda. (Note that only a pre-agenda needs to be specified. The agenda will be automatically generated. A pre-agenda contains all the issues in their unnegated form. The agenda additionally includes their negations.)
- `X, Formula`: For each of the `m` formulas in the pre-agenda, the number `X` as a label followed by the formula.
- `In, Formula`: The input constraint labeled by the string "In". (Note that it is possible to have be multiple input constraints.)
- `Out, Formula`: The output constraint labeled by the string "Out". (Note that it is possible to have be multiple output constraints.)
- `v, j`: The number of voters `v` followed by the number of distinct judgment sets `j`.
- `J, Label_1;...;Label_n`: The number of times this judgment set occurs followed by the labels of the accepted formulas. The formulas should be separated by a semicolon. Issues that are not accepted are rejected.

By starting a line with a "#" the line will be ignored in the reading of the file. Blank lines will also be ignored. Using these comments and blank lines the `.jagg` file can be made more readable.

An example of the format of a `.jagg` file is:
```
x1, x2, x3
4

# The issues
1, x1
2, x2
3, x3
4, ( ~x1 & x2 ) -> x3

# The constraints are the same
In, ( x1 | ~x1 )
Out, ( x1 | ~x1 )

# We have 8 voters and 3 different judgment sets
8, 3
3, 2;3;4
2, 1;2;4
3, 4
```
In this scenario we have the variables `x1`, `x2` and `x3`. There are `4` different issues in the agenda. These issues are `x1`, `x2`, `x3` and `( ~x1 & x2 ) -> x3`, and are labeled by the numbers `1-4` respectively. The input and output constraints are `( x1 | ~x1 )`. There are `8` voters and `3` different judgment sets. Of the voters three have accepted the issues labeled by `2`, `3` and `4` (and thus have rejected the issue labeled by `1`). Two have accepted the issues labeled by `1`, `2` and `4` (and thus have rejected the issue labeled by `3`). And three have accepted the issue labeled by `4` (and thus have rejected the issues labeled by `1`, `2` and `3`).

#### **Creating a Scenario Object**
A scenario object should first be created, and then can be loaded from a `.jagg` file given its path. The path should be given as a string, i.e., of the form `"path/to/file/"`. It can then be loaded using the `load_from_file` method of the scenario class. For example:
```python
from jaggpy import Scenario

scenario1 = Scenario()
scenario1.load_from_file("path/to/file")
```
If there are any inconsistencies in the scenario defined in the `.jagg` file, a warning indicating the inconsistency will occur. It is not possible to successfully load an inconsistent scenario.

#### **Scenario methods and properties**
A scenario object has several useful methods and properties.
- `pretty_repr()`: A method that returns a string that represents the scenario in a readable format.
- `agenda`: This property is a dictionary with the the labels of issues as keys and the issues as values.
- `input_constraints`: This property is a list of the input constraints.
- `output_constraints`: This property is a list of the output constraints.
- `profile`: This property is a list of the judgment sets. Each element is a list of which the first element is the number of times the judgment set occurs. The second element of these lists is a list with the issues that are accepted.
- `number_voters`: This property is an integer specifying the number of voters.

<!-- Solver -->
### Using the solver

#### **Creating a solver object**
In order to call a solver, we first need to create a solver object. We can create a brute force solver object and an ASP solver object as follows:
```python
from jaggpy import BFSolver, ASPSolver
bfs = BFSolver()
asp = ASPSolver()
```

#### **Solver methods**
There are a number of different aggregation rules that are supported. For the brute force solver these are:
- kemeny
- maxhamming
- slater

For the ASP solver these are:
- kemeny
- slater
- leximax
- young
- majority

There are three solver methods corresponding to different ways in which the output is given. For each of these the first argument is the the scenario object and the second argument a lowercase string specifying the rule to be executed. Also, each method has a named argument `verbose` that, if turned on, prints the used rule and solver. This property is `False` by default.

 The methods are the following:
- `all_outcomes()` This method needs no additional arguments. The output of this method is a generator with all the outcomes.
- `outcomes()` This method takes one additional argument `num`, which specifies the number of outcomes that are yielded.

For example, we can compute and enumerate outcomes generated by the Kemeny rule, given the scenario object `scenario1` as follows:

```python
for outcome in asp.all_outcomes(scenario1, "kemeny", verbose=True):
    print(outcome)

for outcome in bfs.outcomes(scenario1, "slater", num=2):
    print(outcome)
```

<!-- Examples -->
<!--
### Examples
The source code of this package contains the folder `src/test`. There are several example files illustrating the use of the `jaggpy` package. It contains several example scenarios, an example python file incorporating the package and explicit ASP encodings of some scenarios and rules.
-->

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.


<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

The encodings in this package are created by [Bo Flachs](https://github.com/BoFlachs), [Philemon Huising](https://github.com/phuising) and [Ronald de Haan](https://staff.science.uva.nl/r.dehaan/)

<!-- CONTACT -->
## Contact

Ronald de Haan - me@ronalddehaan.eu

Github Link: [https://github.com/rdehaan/jaggpy](https://github.com/rdehaan/jaggpy)


<!-- REFERENCES -->
## References
- Endriss, U., de Haan, R., Lang, J., & Slavkovik, M. (2020). [The Complexity Landscape of Outcome Determination in Judgment Aggregation](https://doi.org/10.1613/jair.1.11970). *Journal of Artificial Intelligence Research*, *69*, 687-731.
- de Haan, R., & Slavkovik, M. (2019). [Answer set programming for judgment aggregation](https://doi.org/10.24963/ijcai.2019/231). In *Proceedings of the 28th International Joint Conference on Artificial Intelligence (IJCAI 2019)*. AAAI Press.
