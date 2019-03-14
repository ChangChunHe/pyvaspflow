#!/bin/bash

        sed -n '1,5p' CONTCAR >poscar_img

        echo H >>poscar_img
        echo 1  >>poscar_img
        echo direct >>poscar_img
        echo "0.5 0.5 0.5 "  >>poscar_img

        mkdir image_cor
        mv poscar_img image_cor/POSCAR
        cd image_cor
        Stru_optimation.sh
        cd ..

