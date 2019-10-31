from __future__ import print_function
import LatLon


# position of the sensors
outermost = LatLon.LatLon(LatLon.Latitude(degree=78, minute=21, second=56),
                          LatLon.Longitude(degree=16, minute=48, second=13)),

middle = LatLon.LatLon(LatLon.Latitude(degree=78, minute=22, second=23),
                       LatLon.Longitude(degree=16, minute=53, second=02)),

inside = LatLon.LatLon(LatLon.Latitude(degree=78, minute=23, second=2),
                       LatLon.Longitude(degree=16, minute=57, second=16)),

print(outermost[0].to_string('d% %m% %S% %H'))
print(middle[0].to_string('d% %m% %S% %H'))
print(inside[0].to_string('d% %m% %S% %H'))

outermost_to_middle = (middle[0] - outermost[0])
outermost_to_inside = (inside[0] - outermost[0])

distance_1 = 1e3 * outermost_to_middle.magnitude
angle_1 = outermost_to_middle.heading
distance_2 = 1e3 * outermost_to_inside.magnitude
angle_2 = outermost_to_inside.heading

print("distance outermost to middle: {} m".format(distance_1))
print("heading outermost to middle: {} deg".format(angle_1))
print("distance outermost to inside: {} m".format(distance_2))
print("heading outermost to inside: {} deg".format(angle_2))
