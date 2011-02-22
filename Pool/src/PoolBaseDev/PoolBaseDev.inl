namespace Pool_ns
{

inline const std::string &PoolBaseDev::get_alias()
{
    return alias;
}

inline int PoolBaseDev::get_mov_th_id()
{ 
    return mov_th_id; 
}

inline void PoolBaseDev::pool_shutdown()
{ 
    pool_sd = true; 
}

inline void PoolBaseDev::set_mov_th_id(int t)
{ 
    mov_th_id = t;
}

inline void PoolBaseDev::set_utils(PoolBaseUtil *ptr)
{ 
    utils = ptr;
}

inline ElementId PoolBaseDev::get_id()
{
    assert(id != InvalidId);
    return id; 
}

}	// namespace_ns
