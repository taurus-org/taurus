#include <pool/Constraint.h>

using namespace std;

Constraint::Constraint(const char *inst): Controller(inst)
{
	//cout << "In the Constraint class ctor" << endl;
}

Constraint::~Constraint()
{
	//cout << "In the Constraint class dtor" << endl;
}

