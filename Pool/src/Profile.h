#ifndef _PROFILE_H_
#define _PROFILE_H_

#include <iostream>
#include <stdint.h>

/**
* @brief Class representing a profile node.
* @attention assume-se que o atributo _name � uma cadeia de caracteres est�tica.
*            S� o ponteiro � guardado e comparado por raz�es de efici�ncia
*/
class	ProfileNode {

protected:
	/// N� pai
	ProfileNode* _parent;
	/// N� filho
	ProfileNode* _child;
	/// N� irm�o
	ProfileNode* _sibling;

	/// Nome do n�
	const char*	_name;

	/// N�mero total de chamadas
	int32_t	_totalCalls;
	
	/// Tempo total de execu��o
	double _totalTime;

	/// In�cio de execu��o
	int64_t	_startTime;

	/// Contador de recurs�o
	int	_recursionCounter;

public:
	/** 
	* @brief  Cria um novo n� de Profile associado a um nome e a um n� pai
	* @param  name nome do n� de Profile
	* @param  parent n� pai
	* @attention assume-se que o name � uma cadeia de caracteres est�tica. S� o ponteiro � guardado
	*            e comparado por raz�es de efici�ncia
	*/
	ProfileNode(const char* name, ProfileNode* parent);
	
	/**
	* @brief  Destr�i o n� de Profile
	*/
	~ProfileNode(void);

	/** 
	* @brief  Encontra o n� de Profile com determinado nome
	* @param  name ponteiro est�tico para nome do n� a procurar
	* @return n� correnspondente ao nome dado como argumento
	* @attention assume-se que todos os nomes dos profiles s�o cadeias de caracteres
	* est�ticas e por isso esta fun��o usa o valor do apontador para encontrar o nome
	* do n� e n�o a compara��o de igualdade de conte�do das cadeias.
	*/	
	ProfileNode* getSubNode(const char* name);

	/** 
	* @brief  Devolve o n� pai do n� corrente
	* @return N� pai do n� corrente
	*/
	inline ProfileNode* getParent(void)	 { return _parent;  }

	/** 
	* @brief  Devolve n� irm�o (sibling)
	* @return N� irm�o (sibling)
	*/
	inline ProfileNode* getSibling(void) { return _sibling; }

	/** 
	* @brief  Devolve filho
	* @return N� filho
	*/
	inline ProfileNode* getChild(void)	 { return _child;   }

	/** 
	* @brief  Inicializa este n� de Profile
	*/	
	void reset(void);

	/** 
	* @brief  Chamada ao n�
	*/
	void call(void);

	/** 
	* @brief  Retorno de chamada ao n�
	* @return "true" se o contador de chamadas de fun��o est� a zero. "false" caso contr�rio.
	*/
	bool ret(void);

	/** 
	* @brief  Devolve o nome do n�
	* @return Nome do n�
	*/
	inline const char* getName(void) { return _name; }

	/** 
	* @brief  Obt�m o n�mero total de chamadas
	* @return n�mero total de chamadas
	*/
	inline int32_t getTotalCalls(void)	{ return _totalCalls; }

	/** 
	* @brief  Devolve o tempo total de execu��o correspondente a este n�
	* @return tempo total em milisegundos
	*/
	inline double getTotalTime(void) { return _totalTime; }
};

/**
* @brief Iterador para navegar na �rvore
*/
class ProfileIterator
{
protected:
	/// N� pai actual
	ProfileNode* _currentParent;
	
	/// N� filho actual
	ProfileNode* _currentChild;

	/**
	* @brief Construtor protegido.
	*/
	ProfileIterator(ProfileNode* start);
	
	/// Classe que reconhecer� o construtor protegido.
	friend class ProfileManager;

public:

	/**
	* @brief Devolve o n� pai do iterador actual
	* @return n� de profile pai.
	*/
	ProfileNode* getCurrentParent() { return _currentParent; }
	
	/**
	* @brief Devolve o n� filho actual do iterador.
	* @return n� de profile filho actual.
	*/
	ProfileNode* getCurrentChild()  { return _currentChild; }

	/**
	* @brief  Acesso ao primeiro filho do pai corrente
	*/
	void first(void);

	/**
	* @brief  Acesso ao pr�ximo filho do pai corrente.
	*/
	void next(void);

	/**
	* @brief  Determina se se chegou ao �ltimo filho do pai corrente.
	* @return "true" se n�o existirem mais filhos. "false" caso contr�rio.
	*/
	bool isDone(void);

	/**
	* @brief  Determina se o pai corrente tem filhos.
	* @return "true" se o pai tiver pelo menos um filho. "false" caso contr�rio.
	*/
	bool hasChilds(void);

	/*
	* @brief  Torna o filho dado pelo indice no novo pai.
	* @param  index Ind�ce para o filho que se vai tornar o pai corrente.
	*/
	void enterChild(int index);

	/*
	* @brief  Torna o "maior" filho no pai actual.
	*/
	void enterLargestChild(void);	// Make the largest child the new parent

	/*
	* @brief  Torna o pai do pai actual o novo pai
	*/
	void enterParent(void);			// Make the current parent's parent the new parent.

	// Access the current child

	/*
	* @brief  Acede ao filho actual
	* @return nome do filho actual
	*/
	inline const char* getCurrentName(void){ return _currentChild->getName(); }

	/*
	* @brief  Determina qual o n�mero total de chamadas do filho actual.
	* @return n�mero total de chamadas.
	*/
	inline int getCurrentTotalCalls(void)	{ return _currentChild->getTotalCalls(); }

	/*
	* @brief  Determina qual o tempo de execu��o total do filho actual.
	* @return tempo total do filho actual.
	*/
	inline double getCurrentTotalTime(void)	{ return _currentChild->getTotalTime(); }

	/*
	* @brief  Acede ao pai actual.
	* @return nome do pai actual.
	*/
	inline const char*	getCurrentParentName(void) { return _currentParent->getName(); }

	/*
	* @brief  Determina qual o n�mero total de chamadas do pai actual.
	* @return n�mero total de chamadas.
	*/
	inline int getCurrentParentTotalCalls(void)	 { return _currentParent->getTotalCalls(); }

	/*
	* @brief  Determina qual o tempo de execu��o total do pai actual.
	* @return tempo total do pai actual.
	*/
	inline double getCurrentParentTotalTime(void)	 { return _currentParent->getTotalTime(); }
};


/*
* @brief  Gestor do sistema de Profile.
*/
class	ProfileManager {
private:
	/// N� raiz
	static ProfileNode _root;
	
	/// N� corrente
	static ProfileNode*	_currentNode;
	
	/// Contador de frames
	static int _frameCounter;
	
	/// Instante de reset
	static int64_t _resetTime;

public:
	/**
	* @brief  Devolve o n� raiz do profile.
	* @return N� raiz do profile.
	*/
	static ProfileNode* getRootNode() { return &_root; }

	/*
	* @brief  Iniciar um Profile com determinado nome. Se um filho existe com este nome,
	*         acumula o Profile. Caso contr�rio um novo n� � acrescentado � �rvore de Profile.
	* @param  name nome do Profile
	* @attention assume-se que todos os nomes dos profiles s�o cadeias de caracteres
	* est�ticas e por isso esta fun��o usa o valor do apontador para encontrar o nome
	* do n� e n�o a compara��o de igualdade de conte�do das cadeias.
	*/
	static void startProfile(const char* name);
	
	/*
	* @brief  Parar o temporizador e calcular os resultados
	*/
	static void	stopProfile(void);

	/*
	* @brief  Inicializar o conte�do do sistema de Profile
	*/
	static void reset(void);

	/*
	* @brief  Incrementar o contador de Frames
	*/
	inline static void incrementFrameCounter(void) { _frameCounter++; }

	/*
	* @brief  Obt�m o n�mero de frames desde o �ltimo reset
	* @return n�mero de frames
	*/
	static int getFrameCountSinceReset(void) { return _frameCounter; }

	/*
	* @brief  Obt�m o tempo passado desde o �ltimo reset
	* @return tempo passado
	*/
	static double getTimeSinceReset(void);

	/*
	* @brief  Obt�m o iterador
	*/
	static ProfileIterator*	getIterator(void)	{ return new ProfileIterator( &_root ); }

	/*
	* @brief  Libertar iterador
	*/
	static void releaseIterator(ProfileIterator* iterator) { delete iterator; }

	/*
	* @brief  Fun��o de sistema que retorna o n�mero de ciclos de rel�gio.
	*         Usa interrup��es espec�ficas do pentium
	*/
	static void getTicks(int64_t* ticks);

	/*
	* @brief  Obt�m a frequ�ncia do CPU.
	*         Usa fun��o espec�fica do windows: QueryPerformanceFrequency
	*/
	static double getTickRate(void);
	
	static void getTimer(int64_t *);

	static double getTimerUnit(double *);	
};

/**
* @brief  Proporciona uma forma simples de fazer o profile do scope de uma fun��o.
*         Use a macro PROFILE no in�cio do scope para fazer o c�lculo.
*/
class	ProfileSample {
public:

	/*
	* @brief  Construtor. Inicializa o profile em quest�o.
	* @param  name nome do profile.
	*/
	inline ProfileSample(const char* name) { 
		ProfileManager::startProfile(name); 
	}
	
	/*
	* @brief  Destrutor. Finaliza o profile iniciado
	*/
	inline ~ProfileSample(void) { 
		ProfileManager::stopProfile(); 
	}
};

//#ifdef DEBUG
#define	PROFILE(name) ProfileSample __profile(name)
//#else
//#define	PROFILE(name)
//#endif 

#endif // _PROFILE_H_
