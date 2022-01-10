# AASD

## Dependencies

* Python 3.9

**Important note**: *spade* doesn't yet support Python 3.10 and will fail with 
the error below. 

```
TypeError: As of 3.10, the *loop* parameter was removed from Queue() since it is no longer necessary
```
Use python 3.9. Or if you feel confident you can fix the error manually 
by applying the [patch](python310-spade.patch) to the [spade/behavior.py](https://github.com/javipalanca/spade/blob/master/spade/behaviour.py)

* Docker

## Installing program

```commandline
pip3 install -r requirements.txt
```

To install the requirements to run the unit tests:

```commandline
pip3 install -r dev-requirements.txt
```

## Executing program

```commandline
bash run_docker.sh
python -m src.main
```

## Testing

```commandline
python -m unittest discover test
```