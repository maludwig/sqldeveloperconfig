# SQL Developer Config Tool
================================

### Description

Python tools to help with SQLDeveloper configuration, especially password management

### Installation

Requires Python 3.3+

```bash
pip3 install -r requirements.txt
```

### Usage

Show full help

```bash
python3 -m sqldeveloperconfig --help
python3 -m sqldeveloperconfig auto --help
python3 -m sqldeveloperconfig manual --help
python3 -m sqldeveloperconfig add_connection --help
python3 -m sqldeveloperconfig set_passwords --help
```

Automatic file mode, show all connections and passwords on command line
```bash
  python3 -m sqldeveloperconfig auto
```
Decrypt a specific v4 password
```bash
python3 -m sqldeveloperconfig manual \\
  --encrypted-password mbAyyEhL9pY= \\
  --db-system-id-value 1d5dbbd1-a91e-4298-9a5d-e13b55030b8f
```
Interactively add a connection
```bash
python3 -m sqldeveloperconfig add_connection \\
  --interactive
```
Add a connection from a json config file
```bash
python3 -m sqldeveloperconfig add_connection \\
  --json-files interactive_connection.json
```

Set passwords matching regex
```bash
python3 -m sqldeveloperconfig set_password \\
  --host-regex '^.*localhost.*$' \\
  --user-regex 'system' \\
  --password 'oracle'
```

### Contributing

To run the tests, use:

```bash
python3 -m unittest discover --pattern '*test.py' --verbose .
```
