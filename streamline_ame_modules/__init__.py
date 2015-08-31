# -*- coding: utf-8 -*-

import reports
import products
from products import models
from .products.models.product import update_null_and_slash_codes
import stock
import controllers
import sales
import purchase
import partner
from partner import models
from .partner.models.partner import update_res_partner_is_company
import base