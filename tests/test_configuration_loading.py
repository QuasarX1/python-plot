from pythonplot import load_config

def test_valid():
    cfg = load_config("tests/test_grouping_target.autoplot")
    assert cfg.valid
    print(cfg.namespaces)
    print(cfg.namespace_ids)
    assert "dad9d4fb-a01a-4a25-b95f-dfe20530b085" not in cfg.namespace_ids, "External target of dependancy target has been loaded."
    assert set(cfg.namespace_ids) == { "9edd258b-7909-47d3-988d-ef5ea4a60b36",
                                       "9c9cccc6-cd6f-4e20-9435-f546376f563e",
                                       "53b6732e-d3ce-4c2a-bbfa-9f6f6425a681",
                                       "1dfc4026-7f0d-4422-9436-4e4816163a6a",
                                       "48738452-b6d6-4c8e-a63e-2082bcde32d6",
                                       "a7e0d8f7-ab35-44f2-825e-910fed8fc1a5" }, "Unexpected files were loaded."
