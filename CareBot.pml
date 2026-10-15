mtype = { idle, navigate, fetch, deliver, wait_human, error,
          kitchen, hallway, livingroom };

bool human_near = false;
bool obstacle = false;
bool object_available = true;

/* Robot + Human locations */
mtype robot_loc = hallway;    /* init location */
mtype target_loc = kitchen;   /* where the object is */
mtype human_loc = livingroom; /* init human location */

/* Channels */
chan nav_cmd       = [0] of { mtype };
chan task_cmd      = [0] of { mtype };
chan human_request = [0] of { int };
chan status_ch     = [0] of { mtype };

/* Time simulation */
int time = 0;
int max_wait = 10;



proctype CareObot() {
    mtype state = idle;

    do
    :: state == idle ->
        if
        :: object_available -> { task_cmd ! fetch; state = fetch; }
        :: else -> state = wait_human;
        fi

    :: state == fetch ->
        if
        :: obstacle -> state = error;
        :: else -> nav_cmd ! navigate; state = navigate;
        fi

    :: state == navigate ->
        if
        :: human_near -> state = wait_human;
        :: else -> state = deliver;
        fi

    :: state == wait_human ->
        if
        :: human_near -> skip;     /* keep waiting */
        :: else -> state = deliver;
        fi

    :: state == deliver ->
        if
        :: object_available ->
            object_available = false;
            state = idle;
        :: else ->
            state = error;
        fi

    :: state == error ->
        printf("Error state reached\n");
        break
    od
}


proctype Human() {
    do
    :: /* walk between rooms */
       if
       :: human_loc == livingroom -> human_loc = hallway;
       :: human_loc == hallway    -> human_loc = kitchen;
       :: human_loc == kitchen    -> human_loc = hallway;
       fi

    :: /* proximity detection */
       if
       :: robot_loc == human_loc -> human_near = true;
       :: else -> human_near = false;
       fi

    :: /* occasional request */
       human_request ! 1
    od
}


proctype World() {
    do
    :: obstacle = true
    :: obstacle = false
    od
}


proctype Navigator() {
    mtype cmd;

    do
    :: nav_cmd ? cmd ->
        if
        :: cmd == navigate ->
            /* try to move toward target */
            if
            :: target_loc != robot_loc &&
               ( (robot_loc == hallway && (target_loc == kitchen || target_loc == livingroom)) ||
                 (robot_loc == kitchen  && target_loc == hallway) ||
                 (robot_loc == livingroom && target_loc == hallway) ) ->
                robot_loc = target_loc;
            :: else ->
                /* fallback: move toward hallway */
                if
                :: ( (robot_loc == hallway && (hallway == kitchen || hallway == livingroom)) ||
                     (robot_loc == kitchen  && hallway == hallway) ||
                     (robot_loc == livingroom && hallway == hallway) ) ->
                    robot_loc = hallway;
                :: else ->
                    skip;
                fi
            fi;

            /* report arrival */
            status_ch ! deliver
        fi
    od
}




proctype TaskExec() {
    mtype cmd;

    do
    :: task_cmd ? cmd ->
        if
        :: cmd == fetch ->
            if
            :: robot_loc == target_loc && object_available ->
                skip
            :: else ->
                printf("TaskExec: fetch failed\n");
            fi

        :: cmd == deliver ->
            if
            :: robot_loc == human_loc ->
                printf("TaskExec: delivered to human\n");
            :: else ->
                printf("TaskExec: delivered at robot_loc\n");
            fi
        fi
    od
}


proctype SafetyMonitor() {
    do
    :: (human_near && robot_loc == hallway) ->
        printf("SafetyMonitor: human near in hallway, enforcing stop\n");
        obstacle = true
    od
}


proctype Clock() {
    do
    :: time++
    od
}


init {
    atomic {
        run CareObot();
        run Human();
        run World();
        run Navigator();
        run TaskExec();
        run SafetyMonitor();
        run Clock();
    }
}
