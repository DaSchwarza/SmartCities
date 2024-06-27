(define (problem charge-cars)
  (:domain car-charging)
  (:objects 
    auto1 auto2 auto3 
    station1 station2 
    ; Zeitslots für einen Tag in 5-Minuten-Intervallen
    slot1 slot2 slot3 slot4 slot5 slot6 slot7 slot8 slot9 slot10
    slot11 slot12 slot13 slot14 slot15 slot16 slot17 slot18 slot19 slot20
  )
  (:init 
    (CAR auto1) (CAR auto2) (CAR auto3)
    (STATION station1) (STATION station2)
    ; Zeitslots für einen Tag in 5-Minuten-Intervallen
    (SLOT slot1) (SLOT slot2) (SLOT slot3) (SLOT slot4) (SLOT slot5)
    (SLOT slot6) (SLOT slot7) (SLOT slot8) (SLOT slot9) (SLOT slot10)
    (SLOT slot11) (SLOT slot12) (SLOT slot13) (SLOT slot14) (SLOT slot15)
    (SLOT slot16) (SLOT slot17) (SLOT slot18) (SLOT slot19) (SLOT slot20)
    (at-car-station auto1 station1)
    (at-car-station auto2 station1)
    (at-car-station auto3 station2)
    ; Initial sind alle Slots für beide Stationen verfügbar
    (available station1 slot1) (available station1 slot2) (available station1 slot3)
    (available station1 slot4) (available station1 slot5) (available station1 slot6)
    (available station1 slot7) (available station1 slot8) (available station1 slot9)
    (available station1 slot10) (available station1 slot11) (available station1 slot12)
    (available station1 slot13) (available station1 slot14) (available station1 slot15)
    (available station1 slot16) (available station1 slot17) (available station1 slot18)
    (available station1 slot19) (available station1 slot20)
    (available station2 slot1) (available station2 slot2) (available station2 slot3)
    (available station2 slot4) (available station2 slot5) (available station2 slot6)
    (available station2 slot7) (available station2 slot8) (available station2 slot9)
    (available station2 slot10) (available station2 slot11) (available station2 slot12)
    (available station2 slot13) (available station2 slot14) (available station2 slot15)
    (available station2 slot16) (available station2 slot17) (available station2 slot18)
    (available station2 slot19) (available station2 slot20)
    ; Angenommen, der Strompreis ist in bestimmten Slots niedrig
    (price-low slot3) (price-low slot4) (price-low slot5) (price-low slot6)
    (price-low slot12) (price-low slot20)
    (= (total-cost) 0)
  )
  (:goal 
    (and 
      (charging auto1 slot3) (charging auto2 slot3) (charging auto3 slot3)
      ; oder andere Kombinationen basierend auf Verfügbarkeit und Strompreis
    )
  )
  (:metric minimize (total-cost))
)
