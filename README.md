# JAGGPY

```sh jaggpy``` is a Python package for computing outcomes for [judgement aggregation](https://plato.stanford.edu/entries/belief-merging/#JudAgg). 

<!-- TABLE OF CONTENTS -->
## Table of contents
<ol>
<li>
    <a href="#getting-started">Getting started</a>
    <ul>
    <li><a href="#prerequisites">Prerequisites</a></li>
    <li><a href="#installation">Installation</a></li>
    </ul>
</li>
<li>
    <a href="#usage">Usage</a>
    <ul>
    <li>
        <a href="#scenario-objects">Scenario objects</a>
        <ul>
        <li><a href="#`.jagg-files">`.jagg` files</a></li>
        <li><a href="#creating-a-scenario-object">Creating a scenario object</a></li>
        <li><a href="#`pretty-printing">Pretty printing</a></li>
        <li><a href="#scenario-methods">Scenario methods</a></li>
        </ul>
    </li>
    <li>
        <a href="#using-the-solver">Using the solver</a>
        <ul>
        <li><a href="#creating-a-solver-object">Creating a solver object</a></li>
        <li><a href="#solver-methods">Solver methods</a></li>
        </ul>
    </li>
    <li><a href="#examples">Examples</a></li>
    </ul>
</li>
<li><a href="#license">License</a></li>
<li><a href="#contact">Contact</a></li>
<li><a href="#references">References</a></li>
</ol>

<!-- GETTING STARTED -->
<!-- This still needs to be done! -->
## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* npm
  ```sh
  npm install npm@latest -g
  ```

### Installation

1. Get a free API Key at [https://example.com](https://example.com)
2. Clone the repo
   ```sh
   git clone https://github.com/github_username/repo_name.git
   ```
3. Install NPM packages
   ```sh
   npm install
   ```
4. Enter your API in `config.js`
   ```js
   const API_KEY = 'ENTER YOUR API';
   ```

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- USAGE -->
## Usage
To use this package you need to create a scenario object for the scenario that you want to apply juddgement aggregation to. Futhermore, a solver object needs to be made to apply several aggregation rules to the scenario. These objects and their methods will be discussed in what follows.

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
- `m`: The number of issues in the pre-agenda. (Note that only a pre-agenda needs to be specified. The agenda will be automatically generated.)
- `X, Formula`: For each of the `m` formulas in the pre-agenda, the number `X` as a label followed by the formula.
- `In, Formula`: The input constraint labeled by the string "In". (Note that it is possible to have be multiple input constraints.)
- `Out, Formula`: The output constraint labeled by the string "Out". (Note that it is possible to have be multiple output constraints.)
- `v, j`: The number of voters `v` followed by the number of distinct judgement sets `j`.
- `J, Label_1;...;Label_n`: The number of times this judgement set occurs followed by the labels of the accepted formulas. The formulas should be seperated by a semicolon. The issues that are not accepted will be rejected.

An example of the format of a `.jagg` file is:
```
x1, x2, x3
4
1, x1
2, x2
3, x3
4, ( ~x1 & x2 ) -> x3
In, ( x1 | ~x1 )
Out, ( x1 | ~x1 )
8, 3
3, 2;3;4
2, 1;2;4
3, 4
```
In this scenario we have the variables `x1`, `x2` and `x3`. There are `4` different issues in the agenda. These issues are `x1`, `x2`, `x3` and `( ~x1 & x2 ) -> x3`, and are labeled by the numbers `1-4` respectively. The input and output constraints are `( x1 | ~x1 )`. There are `8` voters and `3` different judgement sets. Of the voters three have accepted the issues labeled by `2`, `3` and `4`. Two have accepted the issues labeled by `1`, `2` and `4`. And three have accepted the issue labeled by `4`.

#### **Creating a Scenario Object**
A scenario object should first be created, and then can be loaded from a `.jagg` file given its path. The path should be a raw string, i.e., of the form `r"path/to/file/"`. It can then be loaded using the `loadFromFile` method of the scenario class. For example:
```python
from jaggpy.classes import Scenario

scenario1 = Scenario()
path = r"path/to/file"
scenario1.loadFromFile(path)
```
If there are any inconsistencies in the scenario defined in the `.jagg` file, a warning indicating the inconsistency will occur. It is not possible to successfully load an inconsistent scenario.

#### **Scenario methods**
A scenario object has several useful methods and properties.
- `prettyPrint()`: A method that prints the scenario in a readable format.
- `agenda`: This property is a dictionary with the the labels of issues as keys and the issues as values.
- `inputConstraints`: This property is a list of the input constraints.
- `outputConstraints`: This property is a list of the output constraints.
- `profile`: This property is a list of the judgement sets. Each element is a list of which the first element is the number of times the judgement set occurs. The second element of these lists is a list with the issues that are accepted.
- `numberVoters`: This property is an integer specifying the number of voters.

<!-- Solver -->
### Using the solver

#### Creating a solver object

#### Solver methods

<!-- Examples -->
### Examples

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

Ronald de Haan - me@ronalddehaan.eu

Github Link: [https://github.com/rdehaan/jaggpy](https://github.com/rdehaan/jaggpy)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- REFERENCES -->
## References

<p align="right">(<a href="#top">back to top</a>)</p>
