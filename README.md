# AASD

## Dependencies

* Python 3.9
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