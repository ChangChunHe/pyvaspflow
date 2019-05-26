# examples


In fact, it is easy to construct your job through this package.

Here we supply some common vasp calculation shell scripts, they are [band.sh](https://github.com/ChangChunHe/Defect-Formation-Calculation/blob/master/pyflow/examples/common_calculations/band.sh), [dos.sh](https://github.com/ChangChunHe/Defect-Formation-Calculation/blob/master/pyflow/examples/common_calculations/dos.sh). You should supply a `POSCAR` file in your current directory.





## defect calculation

You can read my `defect_cal.sh` example to know how to calculate defect formation energy in VASP. You should supply a poscar file in your current directory. If everything goes right, you will finally get the below directory hierarchy.

```
(vasp) [hecc@cmp test_defect_cal]$ tree -d
.
├── C-Si-defect
│   ├── charge_state_0
│   │   └── scf
│   ├── charge_state_1
│   │   └── scf
│   ├── charge_state_-1
│   │   └── scf
│   ├── charge_state_2
│   │   └── scf
│   ├── charge_state_-2
│   │   └── scf
│   ├── task0
│   ├── task1
│   └── task2
├── image_corr
└── supercell
    └── scf
```

This directory hierarchy will support you to use `pyvasp get_def_form_energy` command, which will generate a `defect-log.txt` and plot a `defect-formation-energy.png` figure.

```shell
pyvasp get_def_form_energy . O-Vacc-defect H-Vacc-defect
```
