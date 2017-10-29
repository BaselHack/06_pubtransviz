from __future__ import division

def CHtoWGSlat(x,y):
    """
    Convert CH1903 system to WGS1984 system (latitude)

    :param x: northing
    :param y: easting
    :return: latitude in WGS1984 system

    """
    x_aux = (x - 200000) / 1000000
    y_aux = (y - 600000) / 1000000

    lat = (16.9023892 + (3.238272 * x_aux)) \
          - (0.270978 * pow(y_aux, 2)) \
          - (0.002528 * pow(x_aux, 2)) \
          - (0.0447 * pow(y_aux, 2) * x_aux) \
          - (0.0140 * pow(x_aux, 3))

    lat = (lat * 100) / 36

    return lat

def CHtoWGSlng(x,y):
    """
    Convert CH1903 system to WGS1984 system (longitude)

    :param x: northing
    :param y: easting
    :return: longitude in WGS1984 system

    """
    x_aux = (x - 200000) / 1000000
    y_aux = (y - 600000) / 1000000

    lng = (2.6779094 + (4.728982 * y_aux) + (0.791484 * y_aux * x_aux) +
           (0.1306 * y_aux * pow(x_aux, 2))) - (0.0436 * pow(y_aux, 3))

    lng = (lng * 100) / 36

    return lng

def CH1903toWGS1984(x, y):
  """Converts coordinates from CH1903_LV03 to WGS1984 adopting the code taken from
     method from http://www.swisstopo.admin.ch/internet/swisstopo/de/home/products/software/products/skripts.html

     :param x: x coordinates in degrees in CH1903 (northing)
     :param y: y coordinates in degrees in CH1903 (easting)
     :return: a pair containing the latitude and longitude of the given coordinates, respectively"""

  lat = CHtoWGSlat(x, y)
  lng = CHtoWGSlng(x, y)

  return [lat, lng]


if __name__ == "__main__":
    ''' Example usage for the GPSConverter class.'''

    var = CH1903toWGS1984(266874, 607952)
    print (var)
