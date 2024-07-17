
    (define (domain charging)
      (:requirements :typing :action-costs)
    
      (:types car parkingspot time)
    
      (:predicates 
        (charging ?c - car ?s - parkingspot ?t - time)
        (time-slot ?t - time)
        (car-at ?c - car ?s - parkingspot)
      )
    
      (:functions 
        (total-cost)
        (cost-of ?t - time)
      )
    
      (:action start-charging
        :parameters (?c - car ?s - parkingspot ?t - time)
        :precondition (and (time-slot ?t) (car-at ?c ?s))
        :effect (and (charging ?c ?s ?t)
                     (increase (total-cost) (cost-of ?t)))
      )
    )
    