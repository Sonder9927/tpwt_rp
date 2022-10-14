# set shell := ["fish", "-c"]

vi := "lvim"

# default
hello:
    @echo 'Hello, world!'
    @just --list

r := "tpwt_r"
p := "tpwt_p"

# eidt rust lib.rs
er:
  {{vi}} {{r}}/src/lib.rs

# maturin develop
up:
  cd {{r}}; \
  maturin develop

# edit python scripts
ep:
  {{vi}} {{p}}/tpwt_hello.py

# test
test:
  {{vi}} {{p}}/pysrc
