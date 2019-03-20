#!/bin/bash

if [ -f INCAR ]
then
exit
fi

if [ ! -n "$encut" ]
then	encut=`grep ENMAX POTCAR |sort -k3nr|awk 'NR==1{print $3*1.3}' `;fi
if [ ! -f POTCAR ]
then
echo "NO POTCAR found"
fi

if [ -f POSCAR ]
then
host_name=`awk 'NR==1' POSCAR`
fi

cat > INCAR <<!
System=$host_name
ENCUT=$encut
ISIF=2
ISTART=0
ICHARG=2
NSW=100
IBRION=2
EDIFF=1E-5
EDIFFG=-0.05
ISMEAR=0
NPAR=4
LREAL=Auto
LWAVE=F
LCHARG=F
ALGO=All

!
##################################################################
if [ -n "$vdw" ] && [ $vdw -eq 1 ]
then    echo "LUSE_VDW = .TRUE.;AGGAC = 0.0000;BPARAM=15.7" >>INCAR;fi

if [ -n "$hse" ] && [ $hse -eq 1 ]
then
	AEXX=0.25
	echo "LHFCALC = .TRUE. ; HFSCREEN = 0.2 ; AEXX = $AEXX; TIME = 0.4 ; LDIAG = .TRUE." >>INCAR
	sed -i '/ALGO/c ALGO=D' INCAR
fi

if [ -n "$soc" ] && [ $soc -eq 1 ]
then    echo "LSORBIT = T;LMAXMIX = 4" >>INCAR;fi
