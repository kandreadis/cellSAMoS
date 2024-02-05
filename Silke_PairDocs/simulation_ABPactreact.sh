#!/bin/bash
# *****************************************************************************
# *
# *  This BASH script is a part of tha analysis of the data published in 
# *  the paper: "Universal motion patterns in confluent cell monolayers"
# *  by Silke Henkes, Kaja Kostanjevec, J. Martin Collinson, Rastko Sknepnek, 
# *  and Eric Bertin, Jounral name, vol, page (2019).
# *
# *  Please refer to the document Computational_summary.pdf for a detailed
# *  description of the tasks performed by this script.
# * 
# *****************************************************************************


topdir_code='/data1/shenkes/SAMoS/build/'
#where data saved, scripts, conf files
topdir_out='/data1/shenkes/ABPactreact/'

parfile='plane_mixed_ABPactreact.conf'


v0val='0.3'
#v0val='0.01'
nu='0.1'
L=50
frac='0.5'

# for example
seed=367496
for v0 in ${v0val}
do
        # convert the active temperature value into a driving velocity, T_eff = v_0^2 /nu
        #v0=`echo "sqrt(${temp}*${nu})" | bc -l`
        echo "v0: " ${v0}
        cd ${topdir}
        confdir=${topdir_out}ABPactreact_${frac}/Dr_${nu}/data_v0_${v0}/
        mkdir -p ${confdir}
        # create input file for the soft particle equilibration which serves as samos vertex input file
        # exact same number as soft particle system, 0% polydispersity at packing fraction 1
        # target area per cell will be pi
        python ${topdir_out}plane_obstacles.py -L ${L} -f 0.9 -p 0.3 -n ${frac} -o  ${confdir}mixed.dat


        cd ${confdir}
        # copy configuration file into run directory and edit parameters using sed
        newparfile=plane_mixed_ABPactreact_Dr_${nu}_v_${v0}.conf
        echo ${newparfile}
        cp ${topdir_out}${parfile} ${newparfile}
        sed -i "s|@V0|$v0|" $newparfile
        sed -i "s|@NU|$nu|" $newparfile
        sed -i "s|@L|$L|" $newparfile
        sed -i "s|@L|$L|" $newparfile # because sed is braindead
        seed=$((seed+1))
        sed -i "s|@SEED|$seed|" $newparfile
        echo ${topdir_in}samos ${newparfile}
        ${topdir_code}samos ${newparfile}

done
