
#include <time.h>
#include <Profile.h>

/*** ProfileNode ***/
ProfileNode::ProfileNode(const char* name, ProfileNode* parent) :
	_parent(parent),
	_child(NULL),
	_sibling(NULL),
	_name(name),
	_totalCalls(0),
	_totalTime(0),
	_startTime(0),
	_recursionCounter(0)
{
	reset();
}

ProfileNode::~ProfileNode(void)
{
	delete _child;
	delete _sibling;
}

ProfileNode* ProfileNode::getSubNode(const char* name)
{
	// Encontrar n� com o nome
	ProfileNode* child = _child;
	while (child) {
		if(child->_name == name) {
			return child;
		}
		child = child->_sibling;
	}

	// Se n�o se encontrou, adicionar novo
	ProfileNode* node = new ProfileNode(name, this);
	node->_sibling = _child;
	_child = node;
	return node;
}


void ProfileNode::reset(void)
{
	_totalCalls = 0;
	_totalTime = 0.0f;

	if(_child) 
		_child->reset();
	
	if(_sibling) 
		_sibling->reset();
	
}

void ProfileNode::call(void)
{
	_totalCalls++;
	if(_recursionCounter++ == 0) {
		ProfileManager::getTicks(&_startTime);
	}
}

bool ProfileNode::ret(void)
{
	if( (--_recursionCounter == 0) && (_totalCalls != 0) ) { 
		int64_t time;
		ProfileManager::getTicks(&time);
		time -= _startTime;
		_totalTime += (double)time / ProfileManager::getTickRate();
	}
	return ( _recursionCounter == 0 );
}

/*** ProfileIterator ***/
ProfileIterator::ProfileIterator(ProfileNode* start)
{
	_currentParent = start;
	_currentChild = _currentParent->getChild();
}

bool ProfileIterator::hasChilds(void) 
{
	return (_currentChild->getChild() != NULL);
}

void ProfileIterator::first(void)
{
	_currentChild = _currentParent->getChild();
}

void ProfileIterator::next(void)
{
	_currentChild = _currentChild->getSibling();
}

bool ProfileIterator::isDone(void)
{
	return _currentChild == NULL;
}

void ProfileIterator::enterChild(int index)
{
	_currentChild = _currentParent->getChild();
	while((_currentChild != NULL) && (index != 0)) {
		index--;
		_currentChild = _currentChild->getSibling();
	}

	if (_currentChild != NULL) {
		_currentParent = _currentChild;
		_currentChild = _currentParent->getChild();
	}
}

void ProfileIterator::enterParent(void)
{
	if(_currentParent->getParent() != NULL) {
		_currentParent = _currentParent->getParent();
	}
	_currentChild = _currentParent->getChild();
}

/*** ProfileManager ***/
ProfileNode	ProfileManager::_root( "Root", NULL );
ProfileNode* ProfileManager::_currentNode = &ProfileManager::_root;
int32_t	ProfileManager::_frameCounter = 0;
int64_t ProfileManager::_resetTime = 0;

void ProfileManager::startProfile(const char* name)
{
	if(name != _currentNode->getName()) {
		_currentNode = _currentNode->getSubNode(name);
	} 
	_currentNode->call();
}

void ProfileManager::stopProfile(void)
{
	// "ret" indicar� se devemos voltar ao pai ( se estamos a tratar uma fun��o recursiva)
	if (_currentNode->ret()) {
		_currentNode = _currentNode->getParent();
	}
}

void ProfileManager::reset(void)
{ 
	_root.reset(); 
	_frameCounter = 0;
	getTicks(&_resetTime);
}

double ProfileManager::getTimeSinceReset(void)
{
	int64_t time;
	getTicks(&time);
	time -= _resetTime;
	return (double)time / getTickRate();
}

#ifdef WIN32
inline void ProfileManager::getTicks(int64_t* ticks)
{
	__asm
	{
		push edx;
		push ecx;
		mov ecx,ticks;
		_emit 0Fh
		_emit 31h
		mov [ecx],eax;
		mov [ecx+4],edx;
		pop ecx;
		pop edx;
	}
}

inline double ProfileManager::getTickRate(void)
{
	static double _frequency = -1.0f;
	
	if (_frequency < 0.0f) {
		int64_t curr_rate = 0;
		::QueryPerformanceFrequency ((LARGE_INTEGER *)&curr_rate);
		_frequency = (double)curr_rate;
	} 
	
	return _frequency;
}

inline void ProfileManager::getTimer(int64_t *t)
{
	LARGE_INTEGER li;
	QueryPerformanceCounter(&li);
	*t = li.QuadPart;
}

inline double ProfileManager::getTimerUnit(double *unit)
{
	struct timespec res;
	clock_getres(CLOCK_REALTIME, &res);
	*unit = res.tv_sec + res.tv_nsec*1E-9;
}

#else

/* Returns time in nanoseconds */
inline void ProfileManager::getTicks(int64_t* ticks)
{	
	struct timespec res;
	clock_gettime(CLOCK_REALTIME, &res);
	*ticks = res.tv_sec * 1000000000L + res.tv_nsec;
}

/* Returns the time of one tick */
inline double ProfileManager::getTickRate(void)
{
	struct timespec res;
	clock_getres(CLOCK_REALTIME, &res);
	return res.tv_sec + res.tv_nsec*1E-9;
}

inline void ProfileManager::getTimer(int64_t *t)
{
	struct timespec res;
	clock_gettime(CLOCK_REALTIME, &res);
	*t = res.tv_sec * 1000000000L + res.tv_nsec;
}

inline double ProfileManager::getTimerUnit(double *unit)
{
	struct timespec res;
	clock_getres(CLOCK_REALTIME, &res);
	*unit = res.tv_sec + res.tv_nsec*1E-9;
    return *unit;
}

#endif
