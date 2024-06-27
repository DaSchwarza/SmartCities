(define (domain car-charging)
  (:requirements :strips :fluents :action-costs)
  (:predicates 
    (CAR ?c) 
    (STATION ?s) 
    (SLOT ?t)
    (at-car-station ?c ?s)
    (available ?s ?t) ; Gibt an, ob die Station ?s im Zeitslot ?t verfügbar ist
    (price-low ?t)
    (charging ?c ?t)
  )
  (:functions 
    (total-cost)
  )
  (:action charge-car-low
    :parameters (?c ?s ?t)
    :precondition (and 
      (CAR ?c) (STATION ?s) (SLOT ?t)
      (at-car-station ?c ?s)
      (available ?s ?t)
      (price-low ?t)
    )
    :effect (and 
      (charging ?c ?t)
      (not (available ?s ?t))
      (increase (total-cost) 1)
    )
  )
  (:action charge-car-high
    :parameters (?c ?s ?t)
    :precondition (and 
      (CAR ?c) (STATION ?s) (SLOT ?t)
      (at-car-station ?c ?s)
      (available ?s ?t)
      (not (price-low ?t))
    )
    :effect (and 
      (charging ?c ?t)
      (not (available ?s ?t))
      (increase (total-cost) 5)
    )
  )
)
