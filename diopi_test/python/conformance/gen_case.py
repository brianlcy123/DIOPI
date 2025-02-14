# Copyright (c) 2023, DeepLink.

import os
import sys
import shutil
from .utils import logger
from .model_list import model_op_list
from .config_parser import ConfigParser
from .collect_case import DeviceConfig, CollectCase
from configs import model_config

sys.path.append("../python/configs")


def gen_case(cache_path=".", cur_dir="", model_name="", fname="", impl_folder="", case_output_dir="",
             diopi_case_item_file="diopi_case_items.cfg", device_case_item_file="%s_case_items.cfg"):

    if model_name != "":
        model_name = model_name.lower()
        logger.info(
            f"the op list of {model_name}: {model_op_list[model_name]}"
        )
        diopi_case_item_file = model_name + "_" + diopi_case_item_file
        device_case_item_file = model_name + "_" + device_case_item_file
    else:
        model_name = "diopi"
    diopi_case_item_path = os.path.join(cache_path, model_name, diopi_case_item_file)
    case_output_dir = os.path.join(case_output_dir, model_name + '_case')
    device_case_item_path = os.path.join(case_output_dir, device_case_item_file)

    cfg_parse = ConfigParser(diopi_case_item_path)
    cfg_parse.load(fname)
    cfg_path = diopi_case_item_path

    if os.path.exists(case_output_dir):
        shutil.rmtree(case_output_dir)
    os.makedirs(case_output_dir)

    if impl_folder != "":
        cfg_path = device_case_item_path % os.path.basename(impl_folder)
        sys.path.append(impl_folder)

        from device_configs import device_configs

        opt = DeviceConfig(device_configs)
        opt.run()
        coll = CollectCase(cfg_parse.get_config_cases(), opt.rules())
        coll.collect()
        coll.save(cfg_path)

    from codegen.gen_case import GenConfigTestCase
    gctc = GenConfigTestCase(
        module=model_name, config_path=cfg_path, tests_path=case_output_dir
    )
    gctc.gen_test_cases(fname)
    return gctc.db_case_items
