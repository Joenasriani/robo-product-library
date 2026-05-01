# RoboSafeOS Generated Facility Policy

Generated: sample output
Facility: Sample GCC Business Hotel
Facility type: hotel
Robot type: delivery_robot
Country: united_arab_emirates

## 1. Facility zones

- lobby: Main Lobby | access=public | traffic=high | risk=medium | notes=Peak guest movement during check-in and checkout windows.
- service_corridor: Service Corridor | access=staff_only | traffic=medium | risk=medium | notes=Used by housekeeping and delivery staff.
- guest_floor_12: Guest Floor 12 | access=public | traffic=low | risk=low | notes=Room delivery destination area.
- kitchen_back_of_house: Kitchen Back of House | access=restricted | traffic=high | risk=critical | notes=Excluded from autonomous guest delivery planning.

## 2. Exclusion areas

- kitchen_back_of_house
- staff_changing_rooms
- security_office

## 3. Traffic windows

- 07:00-10:00: high traffic in lobby, service_corridor
- 15:00-18:00: high traffic in lobby

## 4. Task schedule

- room_delivery_evening: Evening guest room delivery | window=18:00-22:00 | zones=service_corridor, guest_floor_12 | staff_review=false

## 5. Package boundary

This document is generated from buyer-provided planning inputs. It is a review artifact for facility, vendor, and integrator discussion. It does not certify a physical deployment or replace site engineering review.
