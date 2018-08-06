# truss-solver
A calculator which determines all unknown forces of a statically determinate truss structure

# before you begin

Before you begin, I will assume you have at least a basic understanding of the Method of Joints in determining the internal forces of a rigid, statically determinate body. If you don't know this method, it's essentially drawing a free-body diagram for each joint in the truss and iteratively solving a large system of equations. For more information, consult https://en.wikibooks.org/wiki/Statics/Method_of_Joints .

# usage

This program works under several crucial restraints:
1. There exist exactly THREE UNKNOWN *external* forces.
2. These unknown forces can be determined using net force and net torque/moment equations in two dimensions by using a 3x4 augmented matrix

#### the json file

The json file is where you're going to put data for each joint in your truss. Here is what the convention looks like:

```
{
  "point_A":
  {
    "coords": [0, 0],
    "forces": {
      "A_x": {
        "is_known" : false,
        "is_internal": false,
        "unit_vector": [1, 0],
        "magnitude": 0
      },
      "A_y": {
        "is_known" : false,
        "is_internal": false,
        "unit_vector": [0, 1],
        "magnitude": 0
      },
      "AB": {
        "is_known" : false,
        "is_internal": true,
        "unit_vector": [1, 0],
        "magnitude": 0
      },
      "AE": {
        "is_known" : false,
        "is_internal": true,
        "unit_vector": [0.5, -0.866025],
        "magnitude": 0
      }
    }
  },
  "point_B":
  {
    "coords": [10, 0],
    "forces": {
      "AB": {
        "is_known" : false,
        "is_internal": true,
        "unit_vector": [-1, 0],
        "magnitude": 0
      },
      "BE": {
        "is_known" : false,
        "is_internal": true,
        "unit_vector": [-0.5, -0.866025],
        "magnitude": 0
      },
      "BD": {
        "is_known" : false,
        "is_internal": true,
        "unit_vector": [0.5, -0.866025],
        "magnitude": 0
      },
      "BC": {
        "is_known" : false,
        "is_internal": true,
        "unit_vector": [1, 0],
        "magnitude": 0
      },
      "weight_B": {
        "is_known": true,
        "is_internal": false,
        "unit_vector": [0, -1],
        "magnitude": 6
      }
    }
  },
  
[some data has been removed for brevity]
  
}
```

**This is a lot of information to walk through**, so let's take this step by step. First, look at the joint for `point_A`. Each joint has two properties:

1. The corrdinate position of the joint
2. A set of forces and their information on the joint.

Essentially, we're representing each joint as a free-body diagram with positional information. The coordinates may be in whatever unit you wish, but just make sure the units are consistent.

Now, let's look at each of the forces within `point_A`. Each force has four properties:

1. The known state (Do you know the magnitude of this force right now?)
2. The internal state (Is this force an internal force, as in, one of the tensile or compressive forces within the truss body?)
3. The unit vector of the force (This program uses the convention of assuming all internal forces are tensile when considering their unit vectors, and will instead use negative magnitude to denote compression.)
4. The magnitude of the force. For forces with unknown magnitude, we arbitrarily set a devault value of `0`.

With this in mind, we can start building our truss structure as a model in which each joint has some of each of the following force types
1. External, known (It's good to have at least one of these)
2. External, unknown (Need exactly three of these)
3. Internal, known (You cannot use these as the starting point of the system solver. Be cautious.)
4. Internal, unknown

For an example of a force with type (1), look at the force `weight_B` in `point_B`. This is a force which is already known, is not internal, has a unit vector pointing straight down, and has a magnitude of 6. You need at least one of these, and you can spread them out to whichever joint you so desire.

For an example of a force with type (2), look at the force `A_x` in `point_A`. This is a force which is unknown, is not internal, has a unit vector pointing straight to the right, and has a default magnitude of `0`. For these forces, it's common to transcribe them from a **pin support** and a **roller support** on the two ends of your truss.

Internally known forces are usually not initially given, but on the off-chance they are, they allow the program to analytically solve some more troublesome joints if the additional value is needed.

For an example of a force with type (4), look at the force `AB` in both `point_A` and `point_B`. Internal forces are a force reaction **pair**, so they need to have opposite direction unit vectors in the different joints. Essentially, we're saying that there exists a member connecting `point_A` to `point_B`, named `AB`, which contains a reactive internal force. Notice that the unit vector for `AB` in `point_A` is `[1, 0]` whereas in `point_B`, the unit vector is flipped in the opposite direction, `[-1, 0]`. Make sure the forces have exactly the same name, i.e., don't use `BA` and stick to ordering letters by lexicographical (alphabetical) order, because otherwise the program will recognize this force as *two different forces* which are **not** a reactive pair.

#### the statics.py file

So you've set up your json file to contain all the forces in your system. Congratulations, the hard part is over. Simply run from the command prompt:

```
python statics.py
```

(Make sure you have Python 3 for this!)

The following will appear in your command prompt:

```
Enter file name for system analysis:
```

Enter the filename of the json file. This is what I did:

```
Enter file name for system analysis: example.json
```

From here, the program will do the rest. Here are the logs of mine:

```
Internal forces:
['AB', 'AE', 'BE', 'BD', 'BC', 'CE', 'CD', 'DE', 'EF']
External forces:
['A_x', 'A_y', 'C']
Processed solution for external forces:
A_x: 51.96150000000001
A_y: 24.0
C: 60.0
Solving: F_y | AE * -0.866025 = -24.0 | Internal force AE: 27.712825842210098
Solving: F_x | AB * 0 = -65.81791292110506 | Internal force AB: -65.81791292110506
{'point_A': {'coords': [0, 0],
             'forces': {'AB': {'is_internal': True,
                               'is_known': True,
                               'magnitude': -65.81791292110506,
                               'unit_vector': [1, 0]},
                        'AE': {'is_internal': True,
                               'is_known': True,
                               'magnitude': 27.712825842210098,
                               'unit_vector': [0.5, -0.866025]},
                        'A_x': {'is_internal': False,
                                'is_known': True,
                                'magnitude': 51.96150000000001,
                                'unit_vector': [1, 0]},
                        'A_y': {'is_internal': False,
                                'is_known': True,
                                'magnitude': 24.0,
                                'unit_vector': [0, 1]}}},

...[some information has been omitted for brevity]...

 'point_E': {'coords': [5, -8.66025],
             'forces': {'AE': {'is_internal': True,
                               'is_known': True,
                               'magnitude': 27.712825842210098,
                               'unit_vector': [-0.5, 0.866025]},
                        'BE': {'is_internal': True,
                               'is_known': False,
                               'magnitude': 0,
                               'unit_vector': [0.5, 0.866025]},
                        'DE': {'is_internal': True,
                               'is_known': False,
                               'magnitude': 0,
                               'unit_vector': [1, 0]},
                        'EF': {'is_internal': True,
                               'is_known': False,
                               'magnitude': 0,
                               'unit_vector': [-0.948683, -0.316228]},
                        'weight_E': {'is_internal': False,
                                     'is_known': True,
                                     'magnitude': 18,
                                     'unit_vector': [0, -1]}}}}
```

The program will then detect which forces are internal and which are external, and use its algorithm to solve this problem. It returns a dictionary which is formatted much in the same way the json file you gave in whas formatted, but this time, all unknown forces are given values. Check for yourself - apparently, force `AB` has a magnitude of `-65.81791292110506`.

Experiment with different truss structures and see what works and what doesn't!
