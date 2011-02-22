
namespace Pool_ns
{


inline void PoolMonitor::get_monitor()
{
    omni_thread *th = omni_thread::self();
    omni_mutex_lock synchronized(*this);

    if (locked_ctr == 0)
    {
        locking_thread = th;
    }
    else if (th != locking_thread)
    {
        int interupted;
        while(locked_ctr > 0)
        {
            interupted = wait(time_out);
            if (interupted == 0)
            {
                Except::throw_exception("GetMonitorTimedOut",
                    "Not able to acquire serialization monitor",
                    "PoolOmniMonitor::get_monitor");
            }
        }
        locking_thread = th;
    }
    else 
    {
    }
    locked_ctr++; 
}

inline void PoolMonitor::rel_monitor()
{
    omni_thread *th = omni_thread::self();
    omni_mutex_lock synchronized(*this);

    if ((locked_ctr == 0) || (th != locking_thread))
        return;
        
    locked_ctr--;
    if (locked_ctr == 0)
    {
        locking_thread = NULL;
        cond.signal();
    }
}

inline int PoolMonitor::wait(int32_t nb_millis)
{
    unsigned long s,n;

    unsigned long nb_sec,nb_nanos;
    nb_sec = nb_millis / 1000 ;
    nb_nanos = (nb_millis - (nb_sec * 1000)) * 1000000;

    omni_thread::get_time(&s, &n, nb_sec, nb_nanos);
    return cond.timedwait(s, n);
}


/**
 * Helper method to print elements of any std object that has a const_iterator
 */
template<class T>
inline void PRINT_ELEMENTS(const T& coll, const char* optcstr="")
{
	typename T::const_iterator pos;
	std::cout << optcstr;
	for(pos = coll.begin(); pos != coll.end() ; pos++)
		std::cout << *pos << ' ';
	std::cout << std::endl;
}

}
