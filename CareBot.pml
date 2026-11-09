mtype = { idle, navigate, fetch, deliver, wait_human, error,
          recover, charge,
          kitchen, hallway, livingroom };

/* environment */
bool human_near = false;
bool obstacle = false;
bool object_available = true;

/* robot + human locations */
mtype robot_loc = hallway;
mtype target_loc = kitchen;
mtype human_loc = livingroom;

/* channels */
chan nav_cmd       = [0] of { mtype };
chan task_cmd      = [0] of { mtype };
chan task_status   = [0] of { mtype };
chan human_request = [0] of { int };
chan status_ch     = [0] of { mtype };

/* time simulation */
int time = 0;
int max_wait = 10;
int wait_start = 0;

/* battery */
int battery = 100;

/* errors */
int error_count = 0;

/* flags */
bool in_error = false;
bool recovering = false;
bool charging = false;
bool delivered = false;

/* task state */
bool carrying = false;
bool has_object = false;

/* mining-friendly propositions */
bool task_active = false;
bool navigation_active = false;
bool waiting_for_human = false;
bool task_completed = false;
bool object_carried = false;
bool low_battery = false;
bool recovery_active = false;

/* safety monitoring */
bool safety_stop = false;


proctype CareObot() {

    mtype state = idle;
    mtype ack;

    do

    :: state == idle ->

        delivered = false;
        task_active = false;
        task_completed = false;

        low_battery = (battery < 30);

        if
        :: battery < 30 ->
            charging = true;
            state = charge

        :: else ->
            if
            :: object_available ->
                task_active = true;
                task_completed = false;
                navigation_active = true;

                nav_cmd ! navigate;
                state = navigate

            :: else ->
                wait_start = time;
                waiting_for_human = true;
                state = wait_human
            fi
        fi


    :: state == navigate ->

        status_ch ? ack;

        navigation_active = false;

        if
        :: human_near ->
            wait_start = time;
            waiting_for_human = true;
            state = wait_human

        :: else ->

            if
            :: battery >= 30 ->
                battery = battery - 30
            :: else ->
                battery = 0
            fi;

            low_battery = (battery < 30);

            task_cmd ! fetch;
            state = fetch
        fi


    :: state == fetch ->

        task_status ? ack;

        if
        :: ack == fetch ->
            state = deliver

        :: ack == error ->
            state = error
        fi


    :: state == wait_human ->

        if
        :: human_near ->
            skip

        :: else ->

            waiting_for_human = false;

            if
            :: has_object && carrying ->
                state = deliver

            :: else ->
                navigation_active = true;
                nav_cmd ! navigate;
                state = navigate
            fi

        :: (time - wait_start) >= max_wait ->
            waiting_for_human = false;
            state = error
        fi


    :: state == deliver ->

        if
        :: has_object && carrying ->

            delivered = true;
            task_completed = true;

            carrying = false;
            has_object = false;

            object_carried = false;

            object_available = false;

            if
            :: battery >= 10 ->
                battery = battery - 10
            :: else ->
                battery = 0
            fi;

            low_battery = (battery < 30);

            state = idle

        :: else ->
            state = error
        fi


    :: state == error ->

        printf("Error state reached\n");

        in_error = true;
        error_count++;

        if
        :: error_count < 3 ->

            recovering = true;
            recovery_active = true;

            if
            :: battery >= 20 ->
                battery = battery - 20
            :: else ->
                battery = 0
            fi;

            low_battery = (battery < 30);

            state = recover

        :: else ->
            printf("Too many errors, stopping\n");
            break
        fi


    :: state == recover ->

        if
        :: obstacle ->
            skip

        :: else ->

            object_available = true;

            recovering = false;
            recovery_active = false;
            in_error = false;

            carrying = false;
            has_object = false;
            object_carried = false;

            state = idle
        fi


    :: state == charge ->

        battery = 100;

        low_battery = false;

        charging = false;

        state = idle

    od
}


proctype Human() {

    do

    :: if
       :: human_loc == livingroom ->
            human_loc = hallway

       :: human_loc == hallway ->
            human_loc = kitchen

       :: human_loc == kitchen ->
            human_loc = hallway
       fi

    :: if
       :: robot_loc == human_loc ->
            human_near = true

       :: else ->
            human_near = false
       fi

    :: if
       :: !object_available ->
            object_available = true

       :: else ->
            skip
       fi

    :: human_request ! 1

    od
}


proctype Navigator() {

    mtype cmd;

    do

    :: nav_cmd ? cmd ->

        if
        :: cmd == navigate ->

            if
            :: target_loc != robot_loc &&
               (
                 (robot_loc == hallway &&
                  (target_loc == kitchen ||
                   target_loc == livingroom))
                 ||
                 (robot_loc == kitchen &&
                  target_loc == hallway)
                 ||
                 (robot_loc == livingroom &&
                  target_loc == hallway)
               ) ->

                robot_loc = target_loc

            :: else ->

                skip
            fi;

            status_ch ! navigate
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
            :: robot_loc == target_loc &&
               object_available ->

                carrying = true;
                has_object = true;

                object_carried = true;

                task_status ! fetch

            :: else ->

                printf("TaskExec: fetch failed\n");

                task_status ! error
            fi


        :: cmd == deliver ->

            if
            :: robot_loc == human_loc ->
                printf("TaskExec: delivered to human\n")

            :: else ->
                printf("TaskExec: delivered at robot_loc\n")
            fi

        fi

    od
}


proctype SafetyMonitor() {

    do

    :: (human_near && robot_loc == hallway && !safety_stop) ->

        safety_stop = true;

        printf("SafetyMonitor: human near in hallway, enforcing stop\n");

        obstacle = true

    :: (!human_near || robot_loc != hallway) && safety_stop ->

        safety_stop = false;

        obstacle = false
    od
}


init {

    atomic {

        run CareObot();
        run Human();
        run Navigator();
        run TaskExec();
        run SafetyMonitor();
    }
}
