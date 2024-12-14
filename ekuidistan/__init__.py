# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Ekuidistan
                                 A QGIS plugin
 Penentuan Garis Ekuidistan dengan Pembobotan Pulau Kecil Untuk Delimitasi Batas Maritim Internasional
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2024-10-19
        copyright            : (C) 2024 by PRGG_8_2024
        email                : krishnaduta12345@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Ekuidistan class from file Ekuidistan.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .ekuidistan import Ekuidistan
    return Ekuidistan(iface)