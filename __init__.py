# -*- coding: utf-8 -*-
"""
/***************************************************************************
 InfoDisplayer
                                 A QGIS plugin
 This plugin aims to showcase relevant informations about your open project
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2025-02-06
        copyright            : (C) 2025 by Hamza widgets Inc.
        email                : hamza.rachidi@ensg.eu
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
    """Load InfoDisplayer class from file InfoDisplayer.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .info_displayer import InfoDisplayer
    return InfoDisplayer(iface)
