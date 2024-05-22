# Quantum Satellite Placement
This quantum algorithm explores the problem of optimally grouping a set of satellites into constellations to observe specific targets on Earth. Each satellite has unique observational capabilities, influencing how effectively it can monitor a designated area for a certain duration. The goal of the algorithm is to demonstrate quantum superiority on how to maximize the Earth coverage of each constellation, ensuring that all targets are monitored as efficiently as possible.

# Usage

1. Launch in Github Codespaces and wait until the codepsace is fully initialised

2. Add your account keys by drag&drop of your dynex.ini into the main folder

3. Verify your account keys by typing the following command in the console:

```
python
>>> import dynex
>>> dynex.test()
>>> exit()
```

Your console will perform tests and validate your account keys. You should see the following message:

```
[DYNEX] TEST RESULT: ALL TESTS PASSED
```

4. Run the demo by typing the following command:

```
python main.py
```

The program will output and save the optimal grouping of the satellites into constellations in the file "result.png".


