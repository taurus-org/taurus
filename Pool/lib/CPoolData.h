#ifndef _CPOOL_DATA_H_
#define _CPOOL_DATA_H_

#include <pthread.h>

namespace Pool_ns
{

/**
 * @brief This class represents a generic single shared data item. 
 * 
 * It is intended to be used in a PoolElement. The idea is to have some data
 * that can be accessed in a thread safe way.
 * 
 * This class should only be used by data that can potentially be accessed by
 * different threads. There is an overhead in setting/getting data since a 
 * synchronization mechanism needed to be put in place in order to prevent 
 * concurrent access to the data.
 *
 * This class can be viewed as a Java synchronized class.
 */
template <typename T>
struct DataItem
{
    /**
     * A constructor. Note the difference in the dy parameter in relation to 
     * Tango. Here the dy specifies the number of rows of data. 
     * So, for example, to have a single element as data dx should be 1 and dy
     * should also be 1. 
     *
     * @param[in] dx number of elements in x dimension (optional) (default is 1)
     * @param[in] dy number of elements in y dimension (optional) default is 1)
     * @param[in] d a pointer to data with which this DataItem should be 
                   initialized (optional) (default is NULL). NULL means the data
                   managed by this DataItem object is not initialized.
     */
    DataItem(int32_t dx = 1, int32_t dy = 1, T* d = NULL)
    { 
        _init(dx, dy, d); 
    }
    
    /**
     * A constructor. Initializes the data with a single element. Useful for
     * single element data.
     *
     * @param[in] data_ref a reference to the data with which this DataItem 
     *             object should be initialized.
     */
    DataItem(T& data_ref)
    {
        _init(1, 1, &data_ref);
        set(data_ref);
    }
    
    /**
     * Copy constructor
     */
    DataItem(const DataItem& di)
    {
        _init(di.dx, di.dy, di.data);
    }
    
    DataItem& operator=(const DataItem& di)
    {
        _init(di.dx, di.dy, data);
        return *this;
    }
    
    /**
     * Destructor
     */
    ~DataItem()
    {
        delete[] data;
    }

    /**
     * Gets a copy of the first element.
     *
     * @return the first element.
     */
    inline T get()
    {
        return geti(0);
    }

    /**
     * Gets a copy of the element located at (x,y).
     *
     * @return the element at (x,y).
     */
    inline T geti(int32_t x, int32_t y)
    {
        return geti(x*(y+1));
    }

    /**
     * Gets a copy of the element located at the specified index.
     *
     * @param[in] index the index 
     * @return the element at the specified index.
     */
    inline T geti(int32_t index)
    {
        pthread_mutex_lock(&mux);
        T d = data[index];
        pthread_mutex_unlock(&mux);
        return d;
    }

    /**
     * Gets a copy of the entire data.
     * 
     * @param[in,out] data_ptr a pointer to the buffer which will contain a 
     *                          copy of this object's data.
     */
    inline void get(T* data_ptr)
    {
        if (!data_ptr)
            return;
            
        pthread_mutex_lock(&mux);
        memcpy(data_ptr, data, size);
        pthread_mutex_unlock(&mux);
    }
    
    /**
     * Changes the first element value of the data to the given value.
     * Useful for setting values of single element data.
     *
     * @param[in] data_ref the new value for the first element.
     */
    inline void set(T& data_ref)
    {
        pthread_mutex_lock(&mux);
        memcpy(data, &data_ref, sizeof(T));
        pthread_mutex_unlock(&mux);
    }
    
    /**
     * Changes the entire data to the given value. The copy is based on the 
     * internal data size.
     *
     * @param[in] data_ptr a pointer to the data to be set.
     */
    inline void set(T* data_ptr)
    {
        pthread_mutex_lock(&mux);
        memcpy(data, data_ptr, size);
        pthread_mutex_unlock(&mux);
    }

    /**
     * Gets the number of elements in the X dimension
     * 
     * @return the number of elements in the X dimension
     */
    inline int32_t getX()  { return dx; }

    /**
     * Gets the number of elements in the Y dimension
     * 
     * @return the number of elements in the Y dimension
     */
    inline int32_t getY()  { return dy; }
    
    /**
     * Gets the total number of elements
     * 
     * @return the total number of elements
     */
    inline int32_t getNb() { return nb_elem; }

protected:
    pthread_mutex_t mux;         ///< the mutex used to synchronize data access
    T*              data;        ///< pointer to the internal data
    int32_t         dx;          ///< number of elements in X dimension
    int32_t         dy;          ///< number of elements in Y dimension
    int32_t         nb_elem;     ///< total number of elements
    int32_t         size;        ///< total size (bytes) of the data
    
    void _init(int32_t x, int32_t y, T* d)
    {   
        dx = x;
        dy = y;
        nb_elem = dx * dy;
        size = nb_elem * sizeof(T);
        data = new T[nb_elem];
        if (d) set(d);
    }    
};

typedef DataItem<int32_t> DataItemState;
typedef DataItem<int32_t> DataItemInt32;
typedef DataItem<int64_t> DataItemInt64;
typedef DataItem<double> DataItemDouble;

}

#endif // _CPOOL_DATA_H_
