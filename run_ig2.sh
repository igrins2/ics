#conda activate igos2n

export IGRINS_CONFIG=/IGRINS/TEST/Config/IGRINS.ini,/IGRINS/TEST/Config/IGRINS_test.ini

PYTHONBIN=/home/ics/miniconda3/envs/igos2n/bin/python

case "$1" in
        obs)
	    (cd ObsApp; $PYTHONBIN ObsApp_gui.py 0)
            ;;
         
        eng)
	    (cd EngTools; $PYTHONBIN EngTools_gui.py)
            ;;
         
        obs-simul)
	    (cd ObsApp; $PYTHONBIN ObsApp_gui.py 1)
            ;;
        *)
            echo $"Usage: $0 {obs|eng|obs-simul}"
            exit 1
esac
